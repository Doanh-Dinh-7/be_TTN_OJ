"""Submission repository. Never delete submission history."""

from uuid import UUID

from app import db
from app.models import Submission, SubmissionResult, SubmissionStatus, UserContestScore


class SubmissionRepository:
    @staticmethod
    def get_by_id(submission_id: UUID) -> Submission | None:
        return db.session.get(Submission, submission_id)

    @staticmethod
    def create(
        user_id: UUID, contest_id: UUID, problem_id: UUID, code: str, language: str
    ) -> Submission:
        s = Submission(
            user_id=user_id,
            contest_id=contest_id,
            problem_id=problem_id,
            code=code,
            language=language,
            status=SubmissionStatus.PENDING,
        )
        db.session.add(s)
        db.session.flush()
        return s

    @staticmethod
    def list_all(
        skip: int = 0, limit: int = 100, contest_id: UUID | None = None
    ) -> list[Submission]:
        q = db.session.query(Submission)
        if contest_id is not None:
            q = q.filter(Submission.contest_id == contest_id)
        return q.order_by(Submission.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def list_by_user_contest(
        user_id: UUID, contest_id: UUID, problem_id: UUID | None = None
    ) -> list[Submission]:
        q = db.session.query(Submission).filter(
            Submission.user_id == user_id,
            Submission.contest_id == contest_id,
        )
        if problem_id is not None:
            q = q.filter(Submission.problem_id == problem_id)
        return q.order_by(Submission.created_at.desc()).all()

    @staticmethod
    def update_status_and_score(submission_id: UUID, status: SubmissionStatus, score: int) -> None:
        s = db.session.get(Submission, submission_id)
        if s:
            s.status = status
            s.score = score

    @staticmethod
    def add_result(
        submission_id: UUID,
        test_case_id: UUID,
        order_index: int,
        status: SubmissionStatus,
        score: int,
        output: str | None,
        error_message: str | None,
        time_ms: int | None,
        memory_mb: float | None,
    ) -> SubmissionResult:
        r = SubmissionResult(
            submission_id=submission_id,
            test_case_id=test_case_id,
            order_index=order_index,
            status=status,
            score=score,
            output=output,
            error_message=error_message,
            time_ms=time_ms,
            memory_mb=memory_mb,
        )
        db.session.add(r)
        db.session.flush()
        return r

    @staticmethod
    def upsert_user_contest_score(
        user_id: UUID, contest_id: UUID, problem_id: UUID, best_score: int, best_submission_id: UUID
    ) -> None:
        row = (
            db.session.query(UserContestScore)
            .filter(
                UserContestScore.user_id == user_id,
                UserContestScore.contest_id == contest_id,
                UserContestScore.problem_id == problem_id,
            )
            .first()
        )
        if row:
            if best_score > row.best_score:
                row.best_score = best_score
                row.best_submission_id = best_submission_id
        else:
            row = UserContestScore(
                user_id=user_id,
                contest_id=contest_id,
                problem_id=problem_id,
                best_score=best_score,
                best_submission_id=best_submission_id,
            )
            db.session.add(row)
