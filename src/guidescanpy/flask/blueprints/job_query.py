import logging
from flask import Blueprint, jsonify, render_template, make_response, abort, request
import pandas as pd
from guidescanpy.tasks import app as tasks_app


bp = Blueprint("job_query", __name__)
logger = logging.getLogger(__name__)


@bp.route("/<job_id>")
def job(job_id):
    result = tasks_app.AsyncResult(job_id)
    if result.status == "SUCCESS" and result.result["queries"]:
        # TODO: Is there a cleaner way to do this?
        first_region = list(result.result["queries"].values())[0]["region"]
    else:
        first_region = ""

    return render_template("job_query.html", result=result, first_region=first_region)


@bp.route("/status/<job_id>")
def status(job_id):
    res = tasks_app.AsyncResult(job_id)
    return jsonify({"status": res.status})


@bp.route("/result/<format>/<job_id>")
def result(format, job_id):
    assert format in ("json", "bed", "csv")
    res = tasks_app.AsyncResult(job_id)
    result = res.result

    # Optional filtering/ordering/pagination
    if "region" in request.args:
        region = request.args["region"]
        assert region in result["queries"], f"Region {region} not found in results"
        value = result["queries"][region]  # value has keys 'region' and 'hits'

        # Create a dataframe for easy ordering/filtering
        hits = pd.DataFrame(value["hits"])
        asc = request.args.get("asc") == "1"
        if orderby := request.args.get("orderby"):
            hits = hits.sort_values(by=orderby, ascending=asc)

        if start := request.args.get("start"):
            start = int(start)
        else:
            start = 0
        if limit := request.args.get("limit"):
            end = start + int(limit)
        else:
            end = None
        hits = hits[start:end]

        hits = hits.to_dict("records")
        # Remove all but the region explicitly requested
        result["queries"] = {region: {"region": value["region"], "hits": hits}}

    match format:
        case "json":
            return jsonify(result)

        case "bed":
            lines = ['track name="guideRNAs"']

            for _, v in result["queries"].items():
                for hit in v["hits"]:
                    chr = hit["coordinate"].split(":")[0]
                    start, end = hit["start"], hit["end"]
                    start -= 1  # convert from 1-indexed inclusive to 0-indexed inclusive; end remains unchanged
                    strand = hit["direction"]
                    region_string = hit["region-string"]
                    lines.append(f"{chr}\t{start}\t{end}\t{region_string}\t0\t{strand}")

            response = "\n".join(lines)
            response = make_response(response, 200)
            response.mimetype = "text/plain"
            return response

        case "csv":
            lines = [
                "Region-name,gRNA-ID,gRNA-SeqNumber of off-targets,"
                "Off-target summary,Cutting efficiency,Specificity,Rank,Coordinates,Strand,Annotations"
            ]

            for _, v in result["queries"].items():
                for i, hit in enumerate(v["hits"], start=1):
                    lines.append(
                        ",".join(
                            str(x)
                            for x in [
                                hit["region-string"],
                                hit["region-string"] + f".{i}",
                                hit["sequence"],
                                hit["n-off-targets"],
                                hit["off-target-summary"],
                                hit["cutting-efficiency"],
                                hit["specificity"],
                                i,
                                hit["coordinate"],
                                hit["direction"],
                                hit["annotations"],
                            ]
                        )
                    )

            response = "\n".join(lines)
            response = make_response(response, 200)
            response.mimetype = "text/csv"
            return response

        case _:
            abort(415)  # Unsupported Media Type


@bp.route("/result/dt/<job_id>")
def result_dt(job_id):
    res = tasks_app.AsyncResult(job_id)
    result = res.result
    region = request.args.get("region")
    value = result["queries"][region]
    hits = pd.DataFrame(value["hits"])
    hits_len = len(hits)

    # Get sorting parameters
    sort_column_num = request.args.get(
        "order[0][column]"
    )  # Default is 0. Can be changed in jQuery code.
    sort_dir = request.args.get("order[0][dir]")  # Default is 'asc'
    if sort_column_num is not None and sort_dir is not None:
        sort_column = request.args.get("columns[" + sort_column_num + "][data]")
        hits.sort_values(by=sort_column, ascending=(sort_dir == "asc"), inplace=True)

    # Get pagination parameters
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 5))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    hits = hits[start_idx:end_idx]
    hits = hits.to_dict("records")

    response = {
        "data": hits,
        "draw": int(request.args.get("draw", 1)),
        "recordsTotal": hits_len,
        "recordsFiltered": hits_len,
    }
    return jsonify(response)
