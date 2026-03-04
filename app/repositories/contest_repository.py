"""Contest repository: DB access only."""

from datetime import datetime, timezone
from uuid import UUID

from app import db
from app.models import Contest, ContestProblem


class ContestRepository:
    @staticmethod
    def get_by_id(contest_id: UUID) -> Contest | None:
        return db.session.get(Contest, contest_id)

    @staticmethod
    def list_public_active() -> list[Contest]:
        now = datetime.now(timezone.utc)
        return (
            db.session.query(Contest)
            .filter(
                Contest.is_public,
                Contest.deleted_at.is_(None),
                Contest.start_time <= now,
                Contest.end_time >= now,
            )
            .order_by(Contest.start_time.desc())
            .all()
        )

    @staticmethod
    def list_all(skip: int = 0, limit: int = 50) -> list[Contest]:
        return (
            db.session.query(Contest)
            .filter(Contest.deleted_at.is_(None))
            .order_by(Contest.start_time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(
        name: str,
        description: str | None,
        start_time: datetime,
        end_time: datetime,
        is_public: bool,
        leaderboard_hidden: bool,
    ) -> Contest:
        c = Contest(
            name=name,
            description=description,
            start_time=start_time,
            end_time=end_time,
            is_public=is_public,
            leaderboard_hidden=leaderboard_hidden,
        )
        db.session.add(c)
        db.session.flush()
        return c

    @staticmethod
    def get_problems(contest_id: UUID) -> list[ContestProblem]:
        return (
            db.session.query(ContestProblem)
            .filter(ContestProblem.contest_id == contest_id)
            .order_by(ContestProblem.order_index)
            .all()
        )
