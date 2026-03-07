"""Problem business logic. Admin only for create."""

import json
import os
import re
import uuid as uuid_lib
from uuid import UUID

from flask import current_app

from app import db
from app.models import AuditLog, ProblemStatus
from app.repositories.problem_repository import ProblemRepository


def _slugify(title: str) -> str:
    """Chuyển title thành slug (lowercase, dấu cách -> gạch ngang, bỏ ký tự đặc biệt)."""
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s or "problem"


def _unique_slug(base_slug: str, exclude_id: UUID | None = None) -> str:
    """Đảm bảo slug unique: nếu đã tồn tại thì thêm -2, -3, ..."""
    from sqlalchemy import select

    from app.models.problem import Problem

    slug = base_slug
    n = 1
    while True:
        q = select(Problem).where(Problem.slug == slug)
        if exclude_id:
            q = q.where(Problem.id != exclude_id)
        if db.session.scalar(q) is None:
            return slug
        n += 1
        slug = f"{base_slug}-{n}"


class ProblemService:
    @staticmethod
    def create_problem(
        title: str,
        description: str,
        input_format: str,
        output_format: str,
        constraints: str,
        time_limit: int,
        memory_limit: int,
        max_score: int,
        created_by: UUID | None,
        language_allowed: str = "python",
    ) -> tuple[dict | None, str | None]:
        """Tạo problem (Admin only)."""
        if time_limit <= 0 or memory_limit <= 0:
            return None, "time_limit và memory_limit phải lớn hơn 0"
        existing = ProblemRepository.get_by_title(title)
        if existing:
            return None, "title đã tồn tại"
        base_slug = _slugify(title)
        slug = _unique_slug(base_slug)
        p = ProblemRepository.create(
            title=title,
            slug=slug,
            description=description,
            input_format=input_format or "",
            output_format=output_format or "",
            constraints=constraints or "",
            time_limit_ms=time_limit,
            memory_limit_mb=memory_limit,
            max_score=max_score,
            created_by=created_by,
            status=ProblemStatus.DRAFT,
            language_allowed=language_allowed,
        )
        db.session.commit()
        return (
            {
                "id": str(p.id),
                "title": p.title,
                "slug": p.slug,
                "description": p.description,
                "input_format": p.input_format,
                "output_format": p.output_format,
                "constraints": p.constraints,
                "time_limit_ms": p.time_limit_ms,
                "memory_limit_mb": p.memory_limit_mb,
                "max_score": p.max_score,
                "status": p.status.value,
                "created_by": str(p.created_by) if p.created_by else None,
            },
            None,
        )

    @staticmethod
    def list_test_cases(problem_id: UUID) -> list[dict]:
        """Danh sách test case của problem (Admin)."""
        items = ProblemRepository.get_test_cases(problem_id)
        return [
            {
                "id": str(tc.id),
                "problem_id": str(problem_id),
                "order_index": tc.order_index,
                "is_sample": tc.is_sample,
                "input": tc.input_data or "",
                "output": tc.expected_output or "",
            }
            for tc in items
        ]

    @staticmethod
    def list_sample_test_cases(problem_id: UUID) -> list[dict]:
        """Danh sách test case mẫu (is_sample=True) của problem (Admin)."""
        items = ProblemRepository.get_test_cases(problem_id)
        return [
            {
                "id": str(tc.id),
                "problem_id": str(problem_id),
                "order_index": tc.order_index,
                "is_sample": tc.is_sample,
                "input": tc.input_data or "",
                "output": tc.expected_output or "",
            }
            for tc in items
            if tc.is_sample
        ]

    @staticmethod
    def add_test_case(
        problem_id: UUID,
        input_data: str | None,
        expected_output: str,
        is_sample: bool = False,
        order_index: int = 0,
        input_path: str | None = None,
        output_path: str | None = None,
    ) -> dict:
        tc = ProblemRepository.add_test_case(
            problem_id=problem_id,
            input_data=input_data,
            expected_output=expected_output,
            is_sample=is_sample,
            order_index=order_index,
            input_path=input_path,
            output_path=output_path,
        )
        db.session.commit()
        return {
            "id": str(tc.id),
            "problem_id": str(problem_id),
            "order_index": tc.order_index,
        }

    @staticmethod
    def delete_test_case(test_case_id: UUID) -> tuple[bool, str | None]:
        """
        Xóa test case (Admin only). Hard delete.
        Business rules: không xóa nếu contest đang chạy; phải còn ít nhất 1 test case.
        """
        tc = ProblemRepository.get_test_case_by_id(test_case_id)
        if not tc:
            return False, "Test case không tồn tại"
        problem_id = tc.problem_id
        count = ProblemRepository.count_test_cases(problem_id)
        if count <= 1:
            return False, "Phải còn ít nhất 1 test case"
        if ProblemRepository.is_problem_in_started_contest(problem_id):
            return False, "Không thể xóa: contest đang chạy"
        ok = ProblemRepository.delete_test_case(test_case_id)
        if not ok:
            return False, "Test case không tồn tại"
        db.session.commit()
        return True, None

    @staticmethod
    def upload_test_case(
        problem_id: UUID,
        input_file,
        output_file,
        is_sample: bool = False,
    ) -> tuple[dict | None, str | None]:
        """
        Upload test case từ file input và output (Admin only).
        Lưu file vào disk, lưu nội dung vào DB để judge dùng.
        Returns (data, None) khi thành công, (None, error_message) khi lỗi.
        """
        if not ProblemRepository.get_by_id(problem_id):
            return None, "Problem không tồn tại"
        if not output_file or not output_file.filename:
            return None, "Thiếu file output (output_file bắt buộc)"
        if not input_file or not input_file.filename:
            return None, "Thiếu file input (input_file bắt buộc)"

        base_dir = current_app.config.get("TEST_CASE_UPLOAD_FOLDER", "test_cases")
        if not os.path.isabs(base_dir):
            base_dir = os.path.join(current_app.instance_path, base_dir)
        problem_dir = os.path.join(base_dir, str(problem_id))
        os.makedirs(problem_dir, exist_ok=True)

        unique = uuid_lib.uuid4().hex[:12]
        input_filename = f"{unique}_in.txt"
        output_filename = f"{unique}_out.txt"
        input_path_abs = os.path.join(problem_dir, input_filename)
        output_path_abs = os.path.join(problem_dir, output_filename)

        try:
            input_file.save(input_path_abs)
            output_file.save(output_path_abs)
        except OSError as e:
            return None, f"Không thể lưu file: {e}"

        try:
            with open(input_path_abs, "r", encoding="utf-8", errors="replace") as f:
                input_data = f.read()
            with open(output_path_abs, "r", encoding="utf-8", errors="replace") as f:
                expected_output = f.read()
        except OSError as e:
            return None, f"Không thể đọc file: {e}"

        rel_input_path = os.path.join(str(problem_id), input_filename)
        rel_output_path = os.path.join(str(problem_id), output_filename)
        order_index = ProblemRepository.get_max_order_index(problem_id)

        tc = ProblemRepository.add_test_case(
            problem_id=problem_id,
            input_data=input_data,
            expected_output=expected_output,
            input_path=rel_input_path,
            output_path=rel_output_path,
            is_sample=is_sample,
            order_index=order_index,
        )
        db.session.commit()
        return (
            {
                "id": str(tc.id),
                "problem_id": str(problem_id),
                "order_index": tc.order_index,
                "input_path": rel_input_path,
                "output_path": rel_output_path,
                "is_sample": is_sample,
            },
            None,
        )

    @staticmethod
    def list_problems_admin(
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
        created_by: UUID | None = None,
        keyword: str | None = None,
    ) -> list[dict]:
        """Danh sách problem cho Admin."""
        status_enum = None
        if status and status.strip().upper() in ("DRAFT", "PUBLISHED"):
            status_enum = ProblemStatus(status.strip().upper())
        items = ProblemRepository.list_all_filtered(
            skip=skip,
            limit=limit,
            status=status_enum,
            created_by=created_by,
            keyword=keyword.strip() if keyword else None,
        )
        problem_ids = [p.id for p in items]
        counts = ProblemRepository.get_non_sample_test_case_counts(problem_ids)
        return [
            {
                "id": str(p.id),
                "title": p.title,
                "slug": p.slug,
                "status": p.status.value,
                "time_limit_ms": p.time_limit_ms,
                "memory_limit_mb": p.memory_limit_mb,
                "max_score": p.max_score,
                "test_case_count": counts.get(p.id, 0),
                "created_by": str(p.created_by) if p.created_by else None,
            }
            for p in items
        ]

    @staticmethod
    def get_problem_for_admin(problem_id: UUID) -> dict | None:
        """Lấy chi tiết problem (Admin). Trả về None nếu không tồn tại hoặc đã bị xóa."""
        p = ProblemRepository.get_by_id(problem_id)
        if not p or p.deleted_at is not None:
            return None
        return {
            "id": str(p.id),
            "title": p.title,
            "slug": p.slug,
            "description": p.description,
            "input_format": p.input_format or "",
            "output_format": p.output_format or "",
            "constraints": p.constraints or "",
            "time_limit_ms": p.time_limit_ms,
            "memory_limit_mb": p.memory_limit_mb,
            "max_score": p.max_score,
            "status": p.status.value,
            "created_by": str(p.created_by) if p.created_by else None,
        }

    @staticmethod
    def get_problem_detail_for_admin(problem_id: UUID) -> dict | None:
        """Chi tiết bài toán"""
        base = ProblemService.get_problem_for_admin(problem_id)
        if not base:
            return None
        test_cases = ProblemService.list_test_cases(problem_id)
        sample_test_cases = ProblemService.list_sample_test_cases(problem_id)
        return {
            **base,
            "test_cases": test_cases,
            "sample_test_cases": sample_test_cases,
        }

    @staticmethod
    def update_problem(
        problem_id: UUID,
        *,
        description: str | None = None,
        input_format: str | None = None,
        output_format: str | None = None,
        constraints: str | None = None,
        time_limit: int | None = None,
        memory_limit: int | None = None,
        max_score: int | None = None,
        updated_by: UUID | None = None,
        ip_address: str | None = None,
    ) -> tuple[dict | None, str | None]:
        """
        Cập nhật problem (Admin only).
        Business rule: không cho sửa nếu problem đang thuộc contest đã bắt đầu.
        """
        p = ProblemRepository.get_by_id(problem_id)
        if not p:
            return None, "Problem không tồn tại"
        if ProblemRepository.is_problem_in_started_contest(problem_id):
            return None, "Không thể sửa: bài toán đang thuộc contest đã bắt đầu"
        if time_limit is not None and time_limit <= 0:
            return None, "time_limit phải lớn hơn 0"
        if memory_limit is not None and memory_limit <= 0:
            return None, "memory_limit phải lớn hơn 0"
        if max_score is not None and max_score <= 0:
            return None, "max_score phải lớn hơn 0"

        old_values = {}
        if description is not None:
            old_values["description"] = p.description
        if input_format is not None:
            old_values["input_format"] = p.input_format
        if output_format is not None:
            old_values["output_format"] = p.output_format
        if constraints is not None:
            old_values["constraints"] = p.constraints
        if time_limit is not None:
            old_values["time_limit_ms"] = p.time_limit_ms
        if memory_limit is not None:
            old_values["memory_limit_mb"] = p.memory_limit_mb
        if max_score is not None:
            old_values["max_score"] = p.max_score

        updated = ProblemRepository.update(
            problem_id,
            description=description,
            input_format=input_format,
            output_format=output_format,
            constraints=constraints,
            time_limit_ms=time_limit,
            memory_limit_mb=memory_limit,
            max_score=max_score,
        )
        if not updated:
            return None, "Problem không tồn tại"

        audit_details = {
            "updated_fields": list(old_values.keys()),
            "old": old_values,
            "new": {
                "description": updated.description if description is not None else None,
                "input_format": updated.input_format if input_format is not None else None,
                "output_format": updated.output_format if output_format is not None else None,
                "constraints": updated.constraints if constraints is not None else None,
                "time_limit_ms": updated.time_limit_ms if time_limit is not None else None,
                "memory_limit_mb": updated.memory_limit_mb if memory_limit is not None else None,
                "max_score": updated.max_score if max_score is not None else None,
            },
        }
        # Bỏ các key có value None trong new
        audit_details["new"] = {k: v for k, v in audit_details["new"].items() if v is not None}

        log = AuditLog(
            user_id=updated_by,
            action="PROBLEM_UPDATE",
            resource="problem",
            resource_id=problem_id,
            details=json.dumps(audit_details, ensure_ascii=False),
            ip_address=ip_address,
        )
        db.session.add(log)
        db.session.commit()
        return (
            {
                "id": str(updated.id),
                "title": updated.title,
                "slug": updated.slug,
                "description": updated.description,
                "input_format": updated.input_format,
                "output_format": updated.output_format,
                "constraints": updated.constraints,
                "time_limit_ms": updated.time_limit_ms,
                "memory_limit_mb": updated.memory_limit_mb,
                "max_score": updated.max_score,
                "status": updated.status.value,
                "created_by": str(updated.created_by) if updated.created_by else None,
            },
            None,
        )

    @staticmethod
    def delete_problem(
        problem_id: UUID,
        *,
        deleted_by: UUID | None = None,
        ip_address: str | None = None,
    ) -> tuple[bool, str | None]:
        """
        Soft delete problem (Admin only). Set deleted_at.
        Returns (True, None) khi thành công, (False, error_message) khi lỗi.
        Business rule: không cho xóa nếu problem đang thuộc contest đã bắt đầu.
        """
        p = ProblemRepository.get_by_id(problem_id)
        if not p:
            return False, "Problem không tồn tại"
        if p.deleted_at is not None:
            return False, "Bài toán đã bị xóa trước đó"
        if ProblemRepository.is_problem_in_started_contest(problem_id):
            return False, "Không thể xóa: bài toán đang thuộc contest đã bắt đầu"
        ok = ProblemRepository.soft_delete(problem_id)
        if not ok:
            return False, "Problem không tồn tại"
        log = AuditLog(
            user_id=deleted_by,
            action="PROBLEM_DELETE",
            resource="problem",
            resource_id=problem_id,
            details=json.dumps({"title": p.title, "slug": p.slug}, ensure_ascii=False),
            ip_address=ip_address,
        )
        db.session.add(log)
        db.session.commit()
        return True, None

    @staticmethod
    def publish_problem(problem_id: UUID) -> tuple[dict | None, str | None]:
        """
        Publish bài toán (Admin only). Chỉ publish khi:
        - Có ít nhất 1 test case
        - Có description (không rỗng)
        - time_limit > 0
        - memory_limit > 0
        """
        p = ProblemRepository.get_by_id(problem_id)
        if not p or p.deleted_at is not None:
            return None, "Problem không tồn tại"
        if p.status == ProblemStatus.PUBLISHED:
            return ProblemService.get_problem_for_admin(problem_id), None
        count = ProblemRepository.count_test_cases(problem_id)
        if count < 1:
            return None, "Không thể publish: chưa có test case"
        if not (p.description or "").strip():
            return None, "Không thể publish: thiếu mô tả (description)"
        if not p.time_limit_ms or p.time_limit_ms <= 0:
            return None, "Không thể publish: time_limit phải lớn hơn 0"
        if not p.memory_limit_mb or p.memory_limit_mb <= 0:
            return None, "Không thể publish: memory_limit phải lớn hơn 0"
        ProblemRepository.update(problem_id, status=ProblemStatus.PUBLISHED)
        db.session.commit()
        return ProblemService.get_problem_for_admin(problem_id), None

    @staticmethod
    def unpublish_problem(problem_id: UUID) -> tuple[dict | None, str | None]:
        """
        Chuyển bài toán từ PUBLISHED về DRAFT (Admin only).
        Không cho unpublish nếu bài toán đang thuộc contest đã bắt đầu.
        """
        p = ProblemRepository.get_by_id(problem_id)
        if not p or p.deleted_at is not None:
            return None, "Bài toán không tồn tại"
        if p.status == ProblemStatus.DRAFT:
            return ProblemService.get_problem_for_admin(problem_id), None
        if ProblemRepository.is_problem_in_started_contest(problem_id):
            return None, "Không thể chuyển về draft: bài toán đang thuộc contest đã bắt đầu"
        ProblemRepository.update(problem_id, status=ProblemStatus.DRAFT)
        db.session.commit()
        return ProblemService.get_problem_for_admin(problem_id), None
