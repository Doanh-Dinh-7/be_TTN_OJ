"""Submission API. Rate limited. Enqueue only; judge in worker."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from uuid import UUID
from app.services.submission_service import SubmissionService
from app.utils.auth import user_required
from app import limiter

submission_bp = Blueprint("submissions", __name__)


def _enqueue_judge(submission_id: str) -> None:
    from app.tasks.judge_task import judge_submission_task  # lazy to avoid circular import
    judge_submission_task.delay(submission_id)


@submission_bp.route("", methods=["POST"])
@jwt_required()
@user_required
@limiter.limit("10 per minute")
def create_submission():
    data = request.get_json() or {}
    code = data.get("code")
    language = data.get("language", "python")
    contest_id_s = data.get("contest_id")
    problem_id_s = data.get("problem_id")
    if not code or not contest_id_s or not problem_id_s:
        return jsonify({"message": "code, contest_id, problem_id required"}), 400
    try:
        contest_id = UUID(contest_id_s)
        problem_id = UUID(problem_id_s)
    except ValueError:
        return jsonify({"message": "Invalid contest_id or problem_id"}), 400
    user_id = UUID(get_jwt_identity())
    result, err = SubmissionService.create_submission(
        user_id, contest_id, problem_id, code, language, _enqueue_judge
    )
    if err:
        return jsonify({"message": err}), 400
    return jsonify(result), 201


@submission_bp.route("/<submission_id>", methods=["GET"])
@jwt_required()
@user_required
def get_submission(submission_id: str):
    try:
        sid = UUID(submission_id)
    except ValueError:
        return jsonify({"message": "Invalid submission id"}), 400
    claims = get_jwt()
    admin = claims.get("role") == "admin"
    user_id = UUID(get_jwt_identity())
    s = SubmissionService.get_submission(sid, user_id, admin=admin)
    if not s:
        return jsonify({"message": "Not found"}), 404
    return jsonify(s), 200


@submission_bp.route("", methods=["GET"])
@jwt_required()
@user_required
def list_my_submissions():
    contest_id_s = request.args.get("contest_id")
    problem_id_s = request.args.get("problem_id")
    if not contest_id_s:
        return jsonify({"message": "contest_id required"}), 400
    try:
        contest_id = UUID(contest_id_s)
    except ValueError:
        return jsonify({"message": "Invalid contest_id"}), 400
    problem_id = UUID(problem_id_s) if problem_id_s else None
    user_id = UUID(get_jwt_identity())
    items = SubmissionService.list_my_submissions(user_id, contest_id, problem_id)
    return jsonify({"submissions": items}), 200
