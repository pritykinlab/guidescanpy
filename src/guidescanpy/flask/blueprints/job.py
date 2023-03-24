import logging
from flask import Blueprint, jsonify
from guidescanpy.tasks import app as tasks_app


bp = Blueprint('job', __name__)
logger = logging.getLogger(__name__)


@bp.route('/status/<job_id>')
def status(job_id):
    res = tasks_app.AsyncResult(job_id)
    return jsonify({'status': res.status})
