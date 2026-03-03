"""Auth API: login, register. No business logic here."""
from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.auth import admin_required, user_required, get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest

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


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    try:
        body = LoginRequest(**data)
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    result, err = AuthService.login(body.email, body.password)
    if err:
        return jsonify({"message": err}), 401
    return jsonify(result), 200


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
