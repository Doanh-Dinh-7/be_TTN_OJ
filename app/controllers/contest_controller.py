"""Contest API. No DB or business logic in routes."""

from uuid import UUID

from flask import Blueprint, jsonify, request

from app.services.contest_service import ContestService
from app.utils.auth import admin_required

contest_bp = Blueprint("contests", __name__)


@contest_bp.route("", methods=["GET"])
def list_contests():
    admin = request.args.get("admin") == "1"
    skip = int(request.args.get("skip", 0))
    limit = min(int(request.args.get("limit", 50)), 100)
    items = ContestService.list_contests(admin=admin, skip=skip, limit=limit)
    return jsonify({"contests": items}), 200


@contest_bp.route("/<contest_id>", methods=["GET"])
def get_contest(contest_id: str):
    try:
        cid = UUID(contest_id)
    except ValueError:
        return jsonify({"message": "Invalid contest id"}), 400
    c = ContestService.get_contest(cid)
    if not c:
        return jsonify({"message": "Contest not found"}), 404
    return jsonify(c), 200


@contest_bp.route("/<contest_id>/problems", methods=["GET"])
def get_contest_problems(contest_id: str):
    try:
        cid = UUID(contest_id)
    except ValueError:
        return jsonify({"message": "Invalid contest id"}), 400
    problems = ContestService.get_contest_problems(cid)
    return jsonify({"problems": problems}), 200


@contest_bp.route("", methods=["POST"])
@admin_required
def create_contest():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"message": "name required"}), 400
    from datetime import datetime

    try:
        start_time = datetime.fromisoformat(data.get("start_time", "").replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(data.get("end_time", "").replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return jsonify({"message": "start_time and end_time required (ISO)"}), 400
    c = ContestService.create_contest(
        name=name,
        description=data.get("description"),
        start_time=start_time,
        end_time=end_time,
        is_public=data.get("is_public", True),
        leaderboard_hidden=data.get("leaderboard_hidden", False),
    )
    return jsonify(c), 201
