"""Admin: quản lý problems và test cases."""

from uuid import UUID

from flask import Blueprint, jsonify, request

from app.services.problem_service import ProblemService
from app.utils.auth import admin_required, get_current_user_id

admin_problems_bp = Blueprint("admin_problems", __name__)


@admin_problems_bp.route("/problems", methods=["GET"])
@admin_required
def list_problems():
    """Danh sách bài toán (Admin only)."""
    skip = int(request.args.get("skip", 0))
    limit = min(int(request.args.get("limit", 50)), 100)
    status = request.args.get("status", "").strip() or None
    keyword = request.args.get("keyword", "").strip() or None
    created_by_raw = request.args.get("created_by", "").strip() or None
    created_by = None
    if created_by_raw:
        try:
            created_by = UUID(created_by_raw)
        except ValueError:
            pass
    items = ProblemService.list_problems_admin(
        skip=skip,
        limit=limit,
        status=status,
        created_by=created_by,
        keyword=keyword,
    )
    return jsonify({"problems": items}), 200


@admin_problems_bp.route("/problems/<problem_id>", methods=["GET"])
@admin_required
def get_problem(problem_id: str):
    """Lấy chi tiết bài toán (Admin only)"""
    try:
        pid = UUID(problem_id)
    except ValueError:
        return jsonify({"message": "Invalid problem_id"}), 400
    result = ProblemService.get_problem_detail_for_admin(pid)
    if result is None:
        return jsonify({"message": "Problem không tồn tại"}), 404
    return jsonify(result), 200


@admin_problems_bp.route("/problems/<problem_id>", methods=["PUT"])
@admin_required
def update_problem(problem_id: str):
    """Chỉnh sửa bài toán (Admin only)."""
    try:
        pid = UUID(problem_id)
    except ValueError:
        return jsonify({"message": "Invalid problem_id"}), 400
    data = request.get_json() or {}
    try:
        from app.schemas.problem import ProblemUpdate

        body = ProblemUpdate(
            description=data.get("description"),
            input_format=data.get("input_format"),
            output_format=data.get("output_format"),
            constraints=data.get("constraints"),
            time_limit=data.get("time_limit"),
            memory_limit=data.get("memory_limit"),
            max_score=data.get("max_score"),
        )
    except (ValueError, TypeError) as e:
        return jsonify({"message": "Dữ liệu không hợp lệ", "detail": str(e)}), 400

    payload = {k: v for k, v in body.model_dump().items() if v is not None}
    if not payload:
        return jsonify({"message": "Không có trường nào để cập nhật"}), 400

    result, err = ProblemService.update_problem(
        pid,
        updated_by=get_current_user_id(),
        ip_address=request.remote_addr,
        **payload,
    )
    if err:
        if "không tồn tại" in (err or "").lower():
            return jsonify({"message": err}), 404
        return jsonify({"message": err}), 400
    return jsonify(result), 200


@admin_problems_bp.route("/problems/<problem_id>/publish", methods=["PATCH"])
@admin_required
def publish_problem(problem_id: str):
    """Publish bài toán (Admin only)."""
    try:
        pid = UUID(problem_id)
    except ValueError:
        return jsonify({"message": "Invalid problem_id"}), 400
    result, err = ProblemService.publish_problem(pid)
    if err:
        if err and "không tồn tại" in err.lower():
            return jsonify({"message": err}), 404
        return jsonify({"message": err}), 400
    return jsonify(result), 200


@admin_problems_bp.route("/problems/<problem_id>/unpublish", methods=["PATCH"])
@admin_required
def unpublish_problem(problem_id: str):
    """Chuyển bài toán từ PUBLISHED về DRAFT (Admin only)."""
    try:
        pid = UUID(problem_id)
    except ValueError:
        return jsonify({"message": "Invalid problem_id"}), 400
    result, err = ProblemService.unpublish_problem(pid)
    if err:
        if err and "không tồn tại" in err.lower():
            return jsonify({"message": err}), 404
        return jsonify({"message": err}), 400
    return jsonify(result), 200


@admin_problems_bp.route("/problems/<problem_id>", methods=["DELETE"])
@admin_required
def delete_problem(problem_id: str):
    """Xóa (soft delete) bài toán (Admin only)."""
    try:
        pid = UUID(problem_id)
    except ValueError:
        return jsonify({"message": "Invalid problem_id"}), 400
    ok, err = ProblemService.delete_problem(
        pid,
        deleted_by=get_current_user_id(),
        ip_address=request.remote_addr,
    )
    if not ok:
        if err and ("không tồn tại" in err.lower() or "đã bị xóa" in err.lower()):
            return jsonify({"message": err}), 404
        return jsonify({"message": err or "Xóa thất bại"}), 400
    return jsonify({"message": "Đã xóa bài toán"}), 200


@admin_problems_bp.route("/problems", methods=["POST"])
@admin_required
def create_problem():
    """Tạo đề (Admin only)."""
    data = request.get_json() or {}
    required = ["title", "description", "time_limit", "memory_limit", "max_score"]
    missing = [k for k in required if k not in data or data[k] is None]
    if not data.get("title") and "title" not in missing:
        missing.append("title")
    if missing:
        return jsonify({"message": "Thiếu thông tin bắt buộc", "fields": missing}), 400

    try:
        from app.schemas.problem import ProblemCreate

        body = ProblemCreate(
            title=str(data["title"]).strip(),
            description=str(data.get("description", "")),
            input_format=data.get("input_format") or "",
            output_format=data.get("output_format") or "",
            constraints=data.get("constraints") or "",
            time_limit=int(data["time_limit"]),
            memory_limit=int(data["memory_limit"]),
            max_score=int(data["max_score"]),
        )
    except (ValueError, TypeError) as e:
        return jsonify({"message": "Dữ liệu không hợp lệ", "detail": str(e)}), 400

    created_by = get_current_user_id()
    result, err = ProblemService.create_problem(
        title=body.title,
        description=body.description,
        input_format=body.input_format,
        output_format=body.output_format,
        constraints=body.constraints,
        time_limit=body.time_limit,
        memory_limit=body.memory_limit,
        max_score=body.max_score,
        created_by=created_by,
    )
    if err:
        return jsonify({"message": err}), 400
    return jsonify(result), 201


# ---------- Test cases ----------


@admin_problems_bp.route("/problems/<problem_id>/testcases", methods=["GET"])
@admin_required
def list_test_cases(problem_id: str):
    """Danh sách test case của bài toán (Admin only)."""
    try:
        pid = UUID(problem_id)
    except ValueError:
        return jsonify({"message": "Invalid problem_id"}), 400
    if not ProblemService.get_problem_for_admin(pid):
        return jsonify({"message": "Problem không tồn tại"}), 404
    items = ProblemService.list_test_cases(pid)
    return jsonify({"test_cases": items}), 200


@admin_problems_bp.route("/problems/<problem_id>/testcases/samples", methods=["GET"])
@admin_required
def list_sample_test_cases(problem_id: str):
    """Danh sách test case mẫu (is_sample=True) của bài toán (Admin only)."""
    try:
        pid = UUID(problem_id)
    except ValueError:
        return jsonify({"message": "Invalid problem_id"}), 400
    if not ProblemService.get_problem_for_admin(pid):
        return jsonify({"message": "Problem không tồn tại"}), 404
    items = ProblemService.list_sample_test_cases(pid)
    return jsonify({"test_cases": items}), 200


@admin_problems_bp.route("/problems/<problem_id>/testcases", methods=["POST"])
@admin_required
def upload_test_case(problem_id: str):
    """Upload test case (input_file + output_file) cho đề (Admin only)."""
    try:
        pid = UUID(problem_id)
    except ValueError:
        return jsonify({"message": "Invalid problem_id"}), 400
    input_file = request.files.get("input_file")
    output_file = request.files.get("output_file")
    is_sample = request.form.get("is_sample", "false").lower() in ("true", "1", "yes")
    result, err = ProblemService.upload_test_case(
        problem_id=pid,
        input_file=input_file,
        output_file=output_file,
        is_sample=is_sample,
    )
    if err:
        return jsonify({"message": err}), 400
    return jsonify(result), 201


@admin_problems_bp.route("/problems/<problem_id>/test-cases", methods=["POST"])
@admin_required
def add_test_case(problem_id: str):
    """Thêm test case (JSON body) cho đề (Admin only)."""
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


@admin_problems_bp.route("/testcases/<testcase_id>", methods=["DELETE"])
@admin_required
def delete_test_case(testcase_id: str):
    """Xóa test case (Admin only). Hard delete."""
    try:
        tcid = UUID(testcase_id)
    except ValueError:
        return jsonify({"message": "Invalid testcase_id"}), 400
    ok, err = ProblemService.delete_test_case(tcid)
    if not ok:
        if err and "không tồn tại" in (err or "").lower():
            return jsonify({"message": err}), 404
        return jsonify({"message": err or "Xóa thất bại"}), 400
    return jsonify({"message": "Đã xóa test case"}), 200
