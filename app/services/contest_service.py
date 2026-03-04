"""Contest business logic. Contest config cannot change after start."""

from datetime import datetime, timezone
from uuid import UUID

from app.repositories.contest_repository import ContestRepository
from app.repositories.problem_repository import ProblemRepository


class ContestService:
    @staticmethod
    def get_contest(contest_id: UUID) -> dict | None:
        c = ContestRepository.get_by_id(contest_id)
        if not c:
            return None
        return {
            "id": str(c.id),
            "name": c.name,
            "description": c.description,
            "start_time": c.start_time.isoformat(),
            "end_time": c.end_time.isoformat(),
            "is_public": c.is_public,
            "leaderboard_hidden": c.leaderboard_hidden,
            "created_at": c.created_at.isoformat(),
        }

    @staticmethod
    def list_contests(admin: bool = False, skip: int = 0, limit: int = 50) -> list[dict]:
        if admin:
            items = ContestRepository.list_all(skip=skip, limit=limit)
        else:
            items = ContestRepository.list_public_active()
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "start_time": c.start_time.isoformat(),
                "end_time": c.end_time.isoformat(),
                "is_public": c.is_public,
            }
            for c in items
        ]

    @staticmethod
    def create_contest(
        name: str,
        description: str | None,
        start_time: datetime,
        end_time: datetime,
        is_public: bool,
        leaderboard_hidden: bool,
    ) -> dict:
        c = ContestRepository.create(
            name, description, start_time, end_time, is_public, leaderboard_hidden
        )
        return {
            "id": str(c.id),
            "name": c.name,
            "start_time": c.start_time.isoformat(),
            "end_time": c.end_time.isoformat(),
        }

    @staticmethod
    def get_contest_problems(contest_id: UUID) -> list[dict]:
        cps = ContestRepository.get_problems(contest_id)
        out = []
        for cp in cps:
            p = ProblemRepository.get_by_id(cp.problem_id)
            if p and not p.deleted_at:
                out.append(
                    {
                        "id": str(p.id),
                        "title": p.title,
                        "order_index": cp.order_index,
                        "max_score": cp.max_score,
                    }
                )
        return out

    @staticmethod
    def is_contest_running(contest_id: UUID) -> bool:
        c = ContestRepository.get_by_id(contest_id)
        if not c:
            return False
        now = datetime.now(timezone.utc)
        return c.start_time <= now <= c.end_time
