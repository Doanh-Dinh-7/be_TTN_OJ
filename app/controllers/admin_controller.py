"""Admin API. Chỉ Admin mới được truy cập."""

from uuid import UUID

from flask import Blueprint, jsonify, request

from app.services.admin_user_service import AdminUserService
from app.services.problem_service import ProblemService
from app.services.submission_service import SubmissionService
from app.utils.auth import admin_required, get_current_user_id

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/submissions", methods=["GET"])
@admin_required
def list_all_submissions():
    """Xem tất cả submission (Admin only)."""
    skip = int(request.args.get("skip", 0))
    limit = min(int(request.args.get("limit", 100)), 200)
    contest_id_s = request.args.get("contest_id")
    contest_id = None
    if contest_id_s:
        try:
            contest_id = UUID(contest_id_s)
        except ValueError:
            return jsonify({"message": "Invalid contest_id"}), 400
    items = SubmissionService.list_all_submissions(skip=skip, limit=limit, contest_id=contest_id)
    return jsonify({"submissions": items}), 200


@admin_bp.route("/problems", methods=["POST"])
@admin_required
def create_problem():
    """Tạo đề (Admin only)."""
    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description", "")
    max_score = data.get("max_score", 100)
    time_limit_ms = data.get("time_limit_ms", 1000)
    memory_limit_mb = data.get("memory_limit_mb", 256)
    language_allowed = data.get("language_allowed", "python")
    if not title:
        return jsonify({"message": "title required"}), 400
    result = ProblemService.create_problem(
        title=title,
        description=description,
        max_score=max_score,
        time_limit_ms=time_limit_ms,
        memory_limit_mb=memory_limit_mb,
        language_allowed=language_allowed,
    )
    return jsonify(result), 201


@admin_bp.route("/problems/<problem_id>/test-cases", methods=["POST"])
@admin_required
def add_test_case(problem_id: str):
    """Thêm test case cho đề (Admin only)."""
    try:
        pid = UUID(problem_id)
    except ValueError:
        return jsonify({"message": "Invalid problem_id"}), 400
    data = request.get_json() or {}
    input_data = data.get("input_data")
    expected_output = data.get("expected_output", "")
    is_sample = data.get("is_sample", False)
    order_index = int(data.get("order_index", 0))
    result = ProblemService.add_test_case(
        problem_id=pid,
        input_data=input_data,
        expected_output=expected_output,
        is_sample=is_sample,
        order_index=order_index,
    )
    return jsonify(result), 201


# ---------- Admin User Management ----------


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """Danh sách user (Admin only)."""
    skip = int(request.args.get("skip", 0))
    limit = min(int(request.args.get("limit", 50)), 100)
    items = AdminUserService.list_users(skip=skip, limit=limit)
    return jsonify({"users": items}), 200


@admin_bp.route("/users/<user_id>/lock", methods=["PATCH"])
@admin_required
def lock_user(user_id: str):
    """Khóa user → không login được. Không xóa submission history."""
    try:
        uid = UUID(user_id)
    except ValueError:
        return jsonify({"message": "Invalid user_id"}), 400
    ok, err = AdminUserService.lock_user(uid)
    if not ok:
        return jsonify({"message": err or "Failed"}), 404
    return jsonify({"message": "User locked"}), 200


@admin_bp.route("/users/<user_id>/unlock", methods=["PATCH"])
@admin_required
def unlock_user(user_id: str):
    """Mở khóa user."""
    try:
        uid = UUID(user_id)
    except ValueError:
        return jsonify({"message": "Invalid user_id"}), 400
    ok, err = AdminUserService.unlock_user(uid)
    if not ok:
        return jsonify({"message": err or "Failed"}), 404
    return jsonify({"message": "User unlocked"}), 200


@admin_bp.route("/users/<user_id>/role", methods=["PATCH"])
@admin_required
def set_user_role(user_id: str):
    """Đổi role user (admin/user). Có hiệu lực ngay. Không cho demote admin cuối cùng."""
    try:
        uid = UUID(user_id)
    except ValueError:
        return jsonify({"message": "Invalid user_id"}), 400
    data = request.get_json() or {}
    role_name = (data.get("role") or "").strip().lower()
    if not role_name:
        return jsonify({"message": "role required"}), 400
    current_admin_id = get_current_user_id()
    ok, err = AdminUserService.set_role(uid, role_name, current_admin_id)
    if not ok:
        if err == "User not found" or err == "Role not found":
            return jsonify({"message": err}), 404
        return jsonify({"message": err}), 400
    return jsonify({"message": "Role updated"}), 200
