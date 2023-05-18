from flask import Blueprint, redirect, url_for, request
from guidescanpy.flask.core.genome import get_genome_structure
from guidescanpy import config

bp = Blueprint("query", __name__)


@bp.route("", methods=["GET"])
def query_endpoint(args={}):
    args = args or request.args
    if config.celery.eager:
        return query(args)
    else:
        from guidescanpy.tasks import query as f

        result = f.delay(args)
        return redirect(url_for("job_query.job", job_id=result.task_id))


def query(args):
    organism = args["organism"]
    enzyme = args["enzyme"]
    topn = int(args["topn"]) if "topn" in args else None
    min_specificity = float(args.get("s-bounds-l", 0))
    min_ce = float(args.get("ce-bounds-l", 0))
    filter_annotated = args.get("filter-annotated", False)
    flanking = int(args.get("flanking", 0))

    genome_structure = get_genome_structure(organism)

    queries = {}
    query_text_or_file = args.get("file") or args.get("query-text")
    regions = genome_structure.parse_regions(query_text_or_file, flanking=flanking)
    for region in regions:
        result = genome_structure.query(
            region,
            enzyme=enzyme,
            topn=topn,
            min_specificity=min_specificity,
            min_ce=min_ce,
            filter_annotated=filter_annotated,
        )
        if result:
            queries[region["region-name"]] = {
                "region": result[0]["region-string"],
                "hits": result,
            }

    return {"organism": organism, "enzyme": enzyme, "queries": queries}
