import subprocess
import re
from flask import jsonify, Blueprint, request
from guidescan import config, __version__
from guidescan.flask.db import conn, create_gene_symbol_query

bp = Blueprint('query', __name__)


def parse_chromosome(line, organism):
    line = line.replace(',', '')
    match = re.match(r'^chr(.*):(\d+)-(\d+)', line)
    if match is not None:
        chr, start, end = match.group(0), match.group(1), match.group(2)
    else:
        return None


def parse_gene_symbol(line, organism):
    return create_gene_symbol_query(line, organism)


def parse_entrez_id(line, organism):
    return None


def parse_line(line, organism):
    return parse_chromosome(line, organism) or parse_gene_symbol(line, organism) or parse_entrez_id(line, organism) or None


@bp.route('', methods=['GET'])
def query():
    # gene_resolver
    # sequence_resolver
    assert 'enzyme' in request.args
    assert 'organism' in request.args
    organism = request.args.get('organism')

    if 'query-text' in request.args:

        results = []
        for line in request.args.get('query-text').split('\n'):
            result = parse_line(line, organism)
            if result is not None:
                result = {
                    'region-name': result['gene_symbol'],
                    'chromosome-name': 'chr' + result['name'],
                    'coords': [result['accession'], result['start_pos'], result['end_pos']]
                }
                results.append(result)

        return jsonify(results)








