"""Admin: quản lý users."""

from uuid import UUID

from flask import Blueprint, jsonify, request

from app.services.admin_user_service import AdminUserService
from app.utils.auth import admin_required, get_current_user_id

admin_users_bp = Blueprint("admin_users", __name__)


@admin_users_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """Danh sách user (Admin only)."""
    skip = int(request.args.get("skip", 0))
    limit = min(int(request.args.get("limit", 50)), 100)
    status = request.args.get("status", "").strip() or None
    role = request.args.get("role", "").strip() or None
    keyword = request.args.get("keyword", "").strip() or None
    verified_raw = request.args.get("verified", "").strip().lower() or None
    verified = None
    if verified_raw in ("true", "1", "yes"):
        verified = True
    elif verified_raw in ("false", "0", "no"):
        verified = False
    items = AdminUserService.list_users(
        skip=skip,
        limit=limit,
        status=status,
        role=role,
        verified=verified,
        keyword=keyword,
    )
    return jsonify({"users": items}), 200


@admin_users_bp.route("/users/<user_id>/lock", methods=["PATCH"])
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


@admin_users_bp.route("/users/<user_id>/unlock", methods=["PATCH"])
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


@admin_users_bp.route("/users/<user_id>/role", methods=["PATCH"])
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
