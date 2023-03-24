import subprocess
import re
from typing import Union
from flask import jsonify, Blueprint, request
from guidescanpy import config, __version__
from guidescanpy.flask.db import conn, create_region_query
from guidescanpy.flask.core.genome import get_genome_structure

bp = Blueprint('query', __name__)


@bp.route('', methods=['GET'])
def query_endpoint(args=None):
    args = args or request.args
    sync = args.get('sync', False)
    if sync:
        results = query(args)
        return jsonify(results)
    else:
        from guidescanpy.tasks import query as f
        result = f.delay(args)
        return jsonify({'job-id': result.id})


def query(args):
    organism = args['organism']
    enzyme = args['enzyme']
    topn = int(args['topn']) if 'topn' in args else None

    genome_structure = get_genome_structure(organism)

    if 'query-text' in args:

        results = []
        for line in args.get('query-text').split('\n'):
            line = line.strip()
            result = genome_structure.query(line, enzyme=enzyme, topn=topn)
            if result is not None:
                results.append(result)

        return results
