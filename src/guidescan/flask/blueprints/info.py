import subprocess
from flask import jsonify, Blueprint, request
from guidescan import config, __version__

bp = Blueprint('info', __name__)


@bp.route('/supported', methods=['GET'])
def supported():
    result = subprocess.run([config.guidescan.bin, "--version"], stdout=subprocess.PIPE)
    guidescan_cli_version = result.stdout.decode('utf-8').strip()
    available = config.json_dict_['guidescan']['grna_database_path_map']

    return jsonify(
        {
            "version": __version__,
            "cli-version": guidescan_cli_version,
            "available": available
        }
    )


@bp.route('/grna_query', methods=['GET'])
def grna_query():
    from guidescan.tasks import grna_query as f
    x = request.args.get('x')
    f.delay(x)
    return 'query queued'


