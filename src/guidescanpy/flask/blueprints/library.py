from flask import Blueprint, redirect, url_for, request

bp = Blueprint("library", __name__)


@bp.route("", methods=["GET"])
def library_endpoint(args={}):
    args = args or request.args
    eager = request.args.get("eager", "0") in ("1", "true", "True")
    eager = True
    if eager:
        return library(args)
    else:
        from guidescanpy.tasks import library as f

        result = f.delay(args)
        return redirect(url_for("job_sequence.job", job_id=result.task_id))


def library(args):
    organism = args["organism"]
    return {"organism": organism, "results": "coming soon"}
