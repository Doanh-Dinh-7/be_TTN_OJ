"""Problem business logic. Admin only for create."""

from uuid import UUID

from app import db
from app.repositories.problem_repository import ProblemRepository


class ProblemService:
    @staticmethod
    def create_problem(
        title: str,
        description: str,
        max_score: int,
        time_limit_ms: int,
        memory_limit_mb: int,
        language_allowed: str = "python",
    ) -> dict:
        p = ProblemRepository.create(
            title=title,
            description=description,
            max_score=max_score,
            time_limit_ms=time_limit_ms,
            memory_limit_mb=memory_limit_mb,
            language_allowed=language_allowed,
        )
        db.session.commit()
        return {
            "id": str(p.id),
            "title": p.title,
            "max_score": p.max_score,
            "time_limit_ms": p.time_limit_ms,
            "memory_limit_mb": p.memory_limit_mb,
        }

    @staticmethod
    def add_test_case(
        problem_id: UUID,
        input_data: str | None,
        expected_output: str,
        is_sample: bool = False,
        order_index: int = 0,
    ) -> dict:
        tc = ProblemRepository.add_test_case(
            problem_id=problem_id,
            input_data=input_data,
            expected_output=expected_output,
            is_sample=is_sample,
            order_index=order_index,
        )
        db.session.commit()
        return {
            "id": str(tc.id),
            "problem_id": str(problem_id),
            "order_index": tc.order_index,
        }
