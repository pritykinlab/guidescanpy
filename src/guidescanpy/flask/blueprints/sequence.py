import os.path
from flask import Blueprint, redirect, url_for, request
from guidescanpy import config
from guidescanpy.core.guidescan import cmd_enumerate

bp = Blueprint("sequence", __name__)


@bp.route("", methods=["GET"])
def sequence_endpoint(args={}):
    args = args or request.args
    eager = request.args.get("eager", "0") in ("1", "true", "True")
    if eager:
        return sequence(args)
    else:
        from guidescanpy.tasks import sequence as f

        result = f.delay(args)
        return redirect(url_for("job_sequence.job", job_id=result.task_id))


def sequence(args):
    organism = args["organism"]
    enzyme = args["enzyme"]

    # TODO: Why is this \r\n and not just \n?
    sequences = args["sequences"].split("\r\n")

    start = False  # match PAM at start instead of at end?
    if enzyme == "cpf1":
        start = True
        pam = "TTTV"
    elif enzyme == "cas9":
        pam = "NGG"
    else:
        raise RuntimeError(f"Unexpected enzyme {enzyme}")

    index_dir = config.guidescan.index_files_path_prefix
    index_prefix = getattr(config.guidescan.index_files_path_map, organism)
    index_prefix = os.path.join(index_dir, index_prefix)

    results = cmd_enumerate(
        kmers=sequences, pam=pam, index_filepath_prefix=index_prefix, start=start
    )

    return {"organism": organism, "enzyme": enzyme, "results": results}
