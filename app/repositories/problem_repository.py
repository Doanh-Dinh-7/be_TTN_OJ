"""Problem and test case repository."""

from uuid import UUID

from app import db
from app.models import ContestProblem, Problem, TestCase


class ProblemRepository:
    @staticmethod
    def get_by_id(problem_id: UUID) -> Problem | None:
        return db.session.get(Problem, problem_id)

    @staticmethod
    def get_test_cases(problem_id: UUID) -> list[TestCase]:
        return (
            db.session.query(TestCase)
            .filter(TestCase.problem_id == problem_id)
            .order_by(TestCase.order_index)
            .all()
        )

    @staticmethod
    def create(
        title: str,
        description: str,
        max_score: int,
        time_limit_ms: int,
        memory_limit_mb: int,
        language_allowed: str,
    ) -> Problem:
        p = Problem(
            title=title,
            description=description,
            max_score=max_score,
            time_limit_ms=time_limit_ms,
            memory_limit_mb=memory_limit_mb,
            language_allowed=language_allowed,
        )
        db.session.add(p)
        db.session.flush()
        return p

    @staticmethod
    def add_test_case(
        problem_id: UUID,
        input_data: str | None,
        expected_output: str,
        is_sample: bool,
        order_index: int,
    ) -> TestCase:
        tc = TestCase(
            problem_id=problem_id,
            input_data=input_data,
            expected_output=expected_output,
            is_sample=is_sample,
            order_index=order_index,
        )
        db.session.add(tc)
        db.session.flush()
        return tc

    @staticmethod
    def get_contest_problem(contest_id: UUID, problem_id: UUID) -> ContestProblem | None:
        return (
            db.session.query(ContestProblem)
            .filter(
                ContestProblem.contest_id == contest_id,
                ContestProblem.problem_id == problem_id,
            )
            .first()
        )
