"""Auth API: login, register, verify email, refresh. No business logic here."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.auth_service import AuthService
from app.utils.auth import admin_required, user_required, get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest, VerifyEmailRequest

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    try:
        body = RegisterRequest(**data)
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    result, err = AuthService.register(body.email, body.password, body.username)
    if err:
        return jsonify({"message": err}), 400
    return jsonify(result), 201


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    data = request.get_json() or {}
    try:
        body = VerifyEmailRequest(**data)
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    result, err = AuthService.verify_email(body.token)
    if err:
        return jsonify({"message": err}), 400
    return jsonify(result), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    try:
        body = LoginRequest(**data)
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    result, err = AuthService.login(body.username, body.password)
    if err:
        return jsonify({"message": err}), 401
    return jsonify(result), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Gửi refresh token trong Authorization: Bearer <refresh_token>, nhận access_token mới (24h)."""
    identity = get_jwt_identity()
    result, err = AuthService.refresh(identity)
    if err:
        return jsonify({"message": err}), 401
    return jsonify(result), 200


@auth_bp.route("/logout", methods=["POST"])
@user_required
def logout():
    """Đăng xuất. Client cần xóa access token sau khi gọi."""
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
@user_required
def me():
    user = get_current_user()
    if not user:
        return jsonify({"message": "Not found"}), 404
    return jsonify({
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "verified": user.verified,
        "role_id": str(user.role_id),
    }), 200
