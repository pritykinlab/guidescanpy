import logging
from flask import Blueprint, jsonify, render_template, abort
from guidescanpy.tasks import app as tasks_app


bp = Blueprint("job_library", __name__)
logger = logging.getLogger(__name__)


@bp.route("/<job_id>")
def job(job_id):
    res = tasks_app.AsyncResult(job_id)
    return render_template(
        "job_library.html", job_id=job_id, status=res.status, result=res.result
    )


@bp.route("/status/<job_id>")
def status(job_id):
    res = tasks_app.AsyncResult(job_id)
    return jsonify({"status": res.status})


@bp.route("/result/<format>/<job_id>")
def result(format, job_id):
    assert format in ("json",)
    res = tasks_app.AsyncResult(job_id)
    result = res.result

    match format:
        case "json":
            return jsonify(result)
        case _:
            abort(415)  # Unsupported Media Type
