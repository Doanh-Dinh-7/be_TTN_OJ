"""Submission business logic. API enqueue only; judge runs in worker."""

from uuid import UUID

from app import db
from app.repositories.problem_repository import ProblemRepository
from app.repositories.submission_repository import SubmissionRepository
from app.services.contest_service import ContestService


class SubmissionService:
    """Validate user/contest/time then enqueue. Do not run judge in API."""

    @staticmethod
    def can_submit(user_id: UUID, contest_id: UUID) -> tuple[bool, str]:
        user = db.session.get(__import__("app.models", fromlist=["User"]).User, user_id)
        if not user:
            return False, "User not found"
        if not user.verified:
            return False, "User must be verified to submit"
        if user.banned:
            return False, "User is banned"
        if not ContestService.is_contest_running(contest_id):
            return False, "Contest is not in progress"
        return True, ""

    @staticmethod
    def create_submission(
        user_id: UUID,
        contest_id: UUID,
        problem_id: UUID,
        code: str,
        language: str,
        enqueue_judge_fn,
    ) -> tuple[dict | None, str | None]:
        ok, err = SubmissionService.can_submit(user_id, contest_id)
        if not ok:
            return None, err
        cp = ProblemRepository.get_contest_problem(contest_id, problem_id)
        if not cp:
            return None, "Problem not in contest"
        problem = ProblemRepository.get_by_id(problem_id)
        if not problem or problem.deleted_at:
            return None, "Problem not found"
        test_cases = ProblemRepository.get_test_cases(problem_id)
        if not test_cases:
            return None, "Problem has no test cases"
        submission = SubmissionRepository.create(user_id, contest_id, problem_id, code, language)
        db.session.commit()
        enqueue_judge_fn(str(submission.id))
        return {
            "id": str(submission.id),
            "problem_id": str(problem_id),
            "contest_id": str(contest_id),
            "status": submission.status.value,
            "score": submission.score,
            "created_at": submission.created_at.isoformat(),
        }, None

    @staticmethod
    def get_submission(
        submission_id: UUID, user_id: UUID | None, admin: bool = False
    ) -> dict | None:
        s = SubmissionRepository.get_by_id(submission_id)
        if not s:
            return None
        if not admin and str(s.user_id) != str(user_id):
            return None
        return {
            "id": str(s.id),
            "problem_id": str(s.problem_id),
            "contest_id": str(s.contest_id),
            "status": s.status.value,
            "score": s.score,
            "created_at": s.created_at.isoformat(),
        }

    @staticmethod
    def list_my_submissions(user_id: UUID, contest_id: UUID, problem_id: UUID | None) -> list[dict]:
        items = SubmissionRepository.list_by_user_contest(user_id, contest_id, problem_id)
        return [
            {
                "id": str(s.id),
                "problem_id": str(s.problem_id),
                "status": s.status.value,
                "score": s.score,
                "created_at": s.created_at.isoformat(),
            }
            for s in items
        ]

    @staticmethod
    def list_all_submissions(
        skip: int = 0, limit: int = 100, contest_id: UUID | None = None
    ) -> list[dict]:
        items = SubmissionRepository.list_all(skip=skip, limit=limit, contest_id=contest_id)
        return [
            {
                "id": str(s.id),
                "user_id": str(s.user_id),
                "contest_id": str(s.contest_id),
                "problem_id": str(s.problem_id),
                "status": s.status.value,
                "score": s.score,
                "created_at": s.created_at.isoformat(),
            }
            for s in items
        ]
