import subprocess
import re
from typing import Union
from flask import jsonify, Blueprint, request
from guidescanpy import config, __version__
from guidescanpy.flask.db import conn, create_region_query
from guidescanpy.flask.core.genome import get_genome_structure

bp = Blueprint('query', __name__)


@bp.route('', methods=['GET'])
def query_endpoint():
    results = query(request.args)
    return jsonify(results)


def query(args):
    organism = args['organism']
    genome_structure = get_genome_structure(organism)

    if 'query-text' in args:

        results = []
        for line in args.get('query-text').split('\n'):
            line = line.strip()
            result = genome_structure.parse_region(line)
            if result is not None:
                results.append(result)

        return results
