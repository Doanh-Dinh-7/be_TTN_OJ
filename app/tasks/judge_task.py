"""
Judge task: run in Celery worker. Execute in isolated Docker only.
Flow: API -> Queue -> Worker -> Docker -> Update DB.
Never run user code directly on server.
"""
from app.celery_app import celery_app
from app import db
from flask import Flask
from app import create_app


@celery_app.task(bind=True)
def judge_submission_task(self, submission_id: str):
    """Run judge in Docker then update submission_results and submission score."""
    app = create_app()
    with app.app_context():
        from uuid import UUID
        from app.models import Submission, SubmissionStatus, SubmissionResult
        from app.repositories.submission_repository import SubmissionRepository
        from app.repositories.problem_repository import ProblemRepository
        from app.judge.docker_runner import run_judge

        sid = UUID(submission_id)
        submission = SubmissionRepository.get_by_id(sid)
        if not submission:
            return {"error": "Submission not found"}
        submission.status = SubmissionStatus.PROCESSING
        db.session.commit()

        test_cases = ProblemRepository.get_test_cases(submission.problem_id)
        problem = ProblemRepository.get_by_id(submission.problem_id)
        if not problem or not test_cases:
            submission.status = SubmissionStatus.RUNTIME_ERROR
            submission.score = 0
            db.session.commit()
            return {"error": "Problem or test cases not found"}

        max_score = problem.max_score
        time_limit_ms = problem.time_limit_ms
        memory_limit_mb = problem.memory_limit_mb
        tc_payload = [
            {"id": str(tc.id), "input": tc.input_data or "", "expected": tc.expected_output, "order": tc.order_index}
            for tc in test_cases
        ]
        results = run_judge(
            code=submission.code,
            language=submission.language,
            test_cases=tc_payload,
            time_limit_ms=time_limit_ms,
            memory_limit_mb=memory_limit_mb,
        )
        passed = sum(1 for r in results if r.get("status") == "accepted")
        total = len(results)
        score = int((passed / total) * max_score) if total else 0
        status = SubmissionStatus.ACCEPTED if passed == total else (
            SubmissionStatus.WRONG_ANSWER if results and results[0].get("status") != "compilation_error"
            else SubmissionStatus.COMPILATION_ERROR
        )
        for i, r in enumerate(results):
            st = r.get("status", "runtime_error")
            if st == "accepted":
                sr_status = SubmissionStatus.ACCEPTED
            elif st == "wrong_answer":
                sr_status = SubmissionStatus.WRONG_ANSWER
            elif st == "time_limit_exceeded":
                sr_status = SubmissionStatus.TIME_LIMIT_EXCEEDED
            elif st == "compilation_error":
                sr_status = SubmissionStatus.COMPILATION_ERROR
            else:
                sr_status = SubmissionStatus.RUNTIME_ERROR
            tc = test_cases[i] if i < len(test_cases) else None
            tc_id = tc.id if tc else (UUID(r.get("test_case_id")) if r.get("test_case_id") else None)
            if not tc_id:
                continue
            SubmissionRepository.add_result(
                submission_id=sid,
                test_case_id=tc_id,
                order_index=r.get("order", i),
                status=sr_status,
                score=max_score // total if st == "accepted" else 0,
                output=r.get("output"),
                error_message=r.get("error"),
                time_ms=r.get("time_ms"),
                memory_mb=r.get("memory_mb"),
            )
        if status == SubmissionStatus.COMPILATION_ERROR:
            score = 0
        SubmissionRepository.update_status_and_score(sid, status, score)
        SubmissionRepository.upsert_user_contest_score(
            submission.user_id, submission.contest_id, submission.problem_id, score, sid
        )
        db.session.commit()
        return {"submission_id": submission_id, "status": status.value, "score": score}
