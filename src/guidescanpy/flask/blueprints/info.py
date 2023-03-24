import subprocess
from flask import jsonify, Blueprint, request
from guidescanpy import config, __version__
from guidescanpy.flask.db import conn

bp = Blueprint('info', __name__)


@bp.route('/supported', methods=['GET'])
def supported():
    result = subprocess.run([config.guidescan.bin, "--version"], stdout=subprocess.PIPE)
    guidescan_cli_version = result.stdout.decode('utf-8').strip()

    available = []
    available_dbs = config.json['guidescan']['grna_database_path_map']
    for organism, v in available_dbs.items():
        for enzyme, _ in v.items():
            available.append({'organism': organism, 'enzyme': enzyme})

    return jsonify(
        {
            "version": __version__,
            "cli-version": guidescan_cli_version,
            "available": available
        }
    )


@bp.route('/examples', methods=['GET'])
def examples():
    return jsonify({
        "coords": {
            "dm6": {
                "cas9": "spn-A\nAct5C\nCdk1\nTor\nZw",
                "cpf1": "spn-A\nAct5C\nCdk1\nTor\nZw"
            },
            "ce11": {
                "cas9": "rad-51\nact-3\ncdk-1\nlet-363\ngspd-1",
                "cpf1": "rad-51\nact-3\ncdk-1\nlet-363\ngspd-1"
            },
            "rn6": {
                "cas9": "rad51\nactb1\nCdk1\nMtor\nG6pd",
                "cpf1": "Rad51\nActb\nCdk1\nMtor\nG6pd"
            },
            "mm39": {
                "cas9": "Rad51\nActb\nCdk1\nMtor\nG6pd",
                "cpf1": "Rad51\nActb\nCdk1\nMtor\nG6pd"
            },
            "sacCer3": {
                "cas9": "RAD51\nACTB\nCDC28\nTOR1\nZWF1",
                "cpf1": "RAD51\nACTB\nCDC28\nTOR1\nZWF1"
            },
            "hg38": {
                "cas9": "RAD51\nACTB\nCDK1\nMTOR\nG6PD",
                "cpf1": "RAD51\nACTB\nCDK1\nMTOR\nG6PD"
            },
            "mm10": {
                "cas9": "Rad51\nActb\nCdk1\nMtor\nG6pd",
                "cpf1": "Rad51\nActb\nCdk1\nMtor\nG6pd"
            }
        },
        "library": {
            "mm39": "Rad51\nActb\nCdk1\nMtor\nG6pd",
            "hg38": "RAD51\nACTB\nCDK1\nMTOR\nG6PD"
        }
    })


@bp.route('/sleep', methods=['GET'])
def sleep():
    from guidescanpy.tasks import sleep as f
    t = request.args.get('t', 1)
    result = f.delay(t)
    return jsonify({'job-id': result.id})





