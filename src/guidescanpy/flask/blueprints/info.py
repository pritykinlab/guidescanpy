import subprocess
from flask import jsonify, Blueprint
from guidescanpy import config, __version__

bp = Blueprint("info", __name__)


@bp.route("/supported", methods=["GET"])
def supported():
    result = subprocess.run([config.guidescan.bin, "--version"], stdout=subprocess.PIPE)
    guidescan_cli_version = result.stdout.decode("utf-8").strip()

    available = []
    available_dbs = config.json["guidescan"]["grna_database_path_map"]
    for organism, v in available_dbs.items():
        for enzyme, _ in v.items():
            available.append({"organism": organism, "enzyme": enzyme})

    return jsonify(
        {
            "version": __version__,
            "cli-version": guidescan_cli_version,
            "available": available,
        }
    )


@bp.route("/example_queries", methods=["GET"])
def example_queries():
    return jsonify(config.json["guidescan"]["example_queries"])


@bp.route("/example_sequences", methods=["GET"])
def example_sequences():
    return jsonify(config.json["guidescan"]["example_sequences"])
