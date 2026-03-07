"""Problem and test case repository."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, or_, select

from app import db
from app.models import Contest, ContestProblem, Problem, ProblemStatus, TestCase
from app.models.base import utc_now


class ProblemRepository:
    @staticmethod
    def get_by_id(problem_id: UUID) -> Problem | None:
        return db.session.get(Problem, problem_id)

    @staticmethod
    def list_all(skip: int = 0, limit: int = 50) -> list[Problem]:
        """Danh sách problem (Admin), bỏ qua soft-deleted."""
        return (
            db.session.query(Problem)
            .filter(Problem.deleted_at.is_(None))
            .order_by(Problem.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def list_all_filtered(
        skip: int = 0,
        limit: int = 50,
        status: ProblemStatus | None = None,
        created_by: UUID | None = None,
        keyword: str | None = None,
    ) -> list[Problem]:
        """Danh sách problem có lọc: status, created_by, keyword (title hoặc slug)."""
        q = db.session.query(Problem).filter(Problem.deleted_at.is_(None))
        if status is not None:
            q = q.filter(Problem.status == status)
        if created_by is not None:
            q = q.filter(Problem.created_by == created_by)
        if keyword and keyword.strip():
            term = f"%{keyword.strip()}%"
            q = q.filter(
                or_(
                    Problem.title.ilike(term),
                    Problem.slug.ilike(term),
                )
            )
        return q.order_by(Problem.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_non_sample_test_case_counts(
        problem_ids: list[UUID],
    ) -> dict[UUID, int]:
        """Số test case không phải sample theo problem_id. Trả về dict problem_id -> count."""
        if not problem_ids:
            return {}
        rows = (
            db.session.query(TestCase.problem_id, func.count(TestCase.id))
            .filter(
                TestCase.problem_id.in_(problem_ids),
                TestCase.is_sample.is_(False),
            )
            .group_by(TestCase.problem_id)
            .all()
        )
        return {pid: count for pid, count in rows}

    @staticmethod
    def get_by_title(title: str) -> Problem | None:
        """Tìm problem theo title (unique)."""
        return db.session.scalar(select(Problem).where(Problem.title == title).limit(1))

    @staticmethod
    def get_test_case_by_id(test_case_id: UUID) -> TestCase | None:
        return db.session.get(TestCase, test_case_id)

    @staticmethod
    def get_test_cases(problem_id: UUID) -> list[TestCase]:
        return (
            db.session.query(TestCase)
            .filter(TestCase.problem_id == problem_id)
            .order_by(TestCase.order_index)
            .all()
        )

    @staticmethod
    def count_test_cases(problem_id: UUID) -> int:
        return db.session.query(TestCase).filter(TestCase.problem_id == problem_id).count()

    @staticmethod
    def delete_test_case(test_case_id: UUID) -> bool:
        """Xóa test case (hard delete). Trả về True nếu đã xóa."""
        tc = db.session.get(TestCase, test_case_id)
        if not tc:
            return False
        db.session.delete(tc)
        db.session.flush()
        return True

    @staticmethod
    def create(
        title: str,
        slug: str,
        description: str,
        input_format: str | None,
        output_format: str | None,
        constraints: str | None,
        time_limit_ms: int,
        memory_limit_mb: int,
        max_score: int,
        created_by: UUID | None,
        status: ProblemStatus = ProblemStatus.DRAFT,
        language_allowed: str = "python",
    ) -> Problem:
        p = Problem(
            title=title,
            slug=slug,
            description=description,
            input_format=input_format or "",
            output_format=output_format or "",
            constraints=constraints or "",
            time_limit_ms=time_limit_ms,
            memory_limit_mb=memory_limit_mb,
            max_score=max_score,
            created_by=created_by,
            status=status,
            language_allowed=language_allowed,
        )
        db.session.add(p)
        db.session.flush()
        return p

    @staticmethod
    def get_max_order_index(problem_id: UUID) -> int:
        """Lấy order_index lớn nhất của test cases thuộc problem (để thêm mới +1)."""
        from sqlalchemy import func

        r = (
            db.session.query(func.coalesce(func.max(TestCase.order_index), -1))
            .filter(TestCase.problem_id == problem_id)
            .scalar()
        )
        return int(r) + 1

    @staticmethod
    def add_test_case(
        problem_id: UUID,
        input_data: str | None,
        expected_output: str,
        is_sample: bool,
        order_index: int,
        input_path: str | None = None,
        output_path: str | None = None,
    ) -> TestCase:
        tc = TestCase(
            problem_id=problem_id,
            input_data=input_data,
            expected_output=expected_output,
            input_path=input_path,
            output_path=output_path,
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

    @staticmethod
    def is_problem_in_started_contest(problem_id: UUID) -> bool:
        """True nếu problem thuộc ít nhất một contest đã bắt đầu (start_time <= now UTC)."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(1)
            .select_from(ContestProblem)
            .join(Contest, Contest.id == ContestProblem.contest_id)
            .where(
                ContestProblem.problem_id == problem_id,
                Contest.start_time <= now,
                Contest.deleted_at.is_(None),
            )
            .limit(1)
        )
        return db.session.scalar(stmt) is not None

    @staticmethod
    def update(
        problem_id: UUID,
        *,
        description: str | None = None,
        input_format: str | None = None,
        output_format: str | None = None,
        constraints: str | None = None,
        time_limit_ms: int | None = None,
        memory_limit_mb: int | None = None,
        max_score: int | None = None,
        status: ProblemStatus | None = None,
    ) -> Problem | None:
        """Cập nhật các trường được phép."""
        p = db.session.get(Problem, problem_id)
        if not p:
            return None
        if description is not None:
            p.description = description
        if input_format is not None:
            p.input_format = input_format
        if output_format is not None:
            p.output_format = output_format
        if constraints is not None:
            p.constraints = constraints
        if time_limit_ms is not None:
            p.time_limit_ms = time_limit_ms
        if memory_limit_mb is not None:
            p.memory_limit_mb = memory_limit_mb
        if max_score is not None:
            p.max_score = max_score
        if status is not None:
            p.status = status
        db.session.flush()
        return p

    @staticmethod
    def soft_delete(problem_id: UUID) -> bool:
        """Soft delete: set deleted_at."""
        p = db.session.get(Problem, problem_id)
        if not p or p.deleted_at is not None:
            return False
        p.deleted_at = utc_now()
        db.session.flush()
        return True
