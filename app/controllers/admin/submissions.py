"""Admin: quản lý submissions."""

from uuid import UUID

from flask import Blueprint, jsonify, request

from app.services.submission_service import SubmissionService
from app.utils.auth import admin_required

admin_submissions_bp = Blueprint("admin_submissions", __name__)


@admin_submissions_bp.route("/submissions", methods=["GET"])
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
