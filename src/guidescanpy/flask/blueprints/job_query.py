import logging
from flask import Blueprint, jsonify, render_template, make_response, abort, request
import pandas as pd
from guidescanpy.tasks import app as tasks_app


bp = Blueprint("job_query", __name__)
logger = logging.getLogger(__name__)


@bp.route("/<job_id>")
def job(job_id):
    result = tasks_app.AsyncResult(job_id)
    if result.status == "SUCCESS":
        # TODO: Is there a cleaner way to do this?
        first_region = (
            list(result.result["queries"].values())[0]["region"]
            if ("queries" in result.result) and result.result["queries"]
            else ""
        )
        overwhelming_err = (
            result.result["overwhelming_err"]
            if "overwhelming_err" in result.result
            else ""
        )
    else:
        first_region, overwhelming_err = "", ""
    return render_template(
        "job_query.html",
        result=result,
        first_region=first_region,
        overwhelming_err=overwhelming_err,
    )


@bp.route("/status/<job_id>")
def status(job_id):
    res = tasks_app.AsyncResult(job_id)
    return jsonify({"status": res.status})


def get_result(
    job_id, region=None, start=0, end=None, orderby=None, asc=True, dt=False
):
    """
    return a full result dictionary for non-DataTable use, a 'hits' dictionary for DataTable use.
    """
    res = tasks_app.AsyncResult(job_id)
    result = res.result
    if region is None:
        return result
    assert region in result["queries"], f"Region {region} not found in results"
    value = result["queries"][region]
    hits = pd.DataFrame(value["hits"])
    hits_len = len(hits)
    if orderby:
        hits.sort_values(by=orderby, ascending=asc, inplace=True)
    hits = hits[start:end]
    hits = hits.to_dict("records")
    if dt:
        return hits, hits_len
    else:
        result["queries"] = {region: {"region": value["region"], "hits": hits}}
        return result


@bp.route("/result/<format>/<job_id>")
def result(format, job_id):
    region = request.args.get("region")
    orderby = request.args.get("orderby")
    asc = request.args.get("asc") == "asc"
    start = int(request.args.get("start", 0))
    end = (
        int(request.args.get("limit")) + start
        if request.args.get("limit") is not None
        else None
    )
    result = get_result(job_id, region, start, end, orderby, asc, dt=False)

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
                "Off-target summary,Cutting efficiency,Specificity,GC,Rank,Coordinates,Strand,Annotations"
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
                                hit["gc-content"],
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
    region = request.args.get("region")

    # Get sorting parameters
    orderby = request.args.get("order[0][column]")  # Default is 5.
    if orderby is not None:
        orderby = request.args.get("columns[" + orderby + "][data]")
    asc = request.args.get("order[0][dir]") == "asc"  # Default is 'desc'

    # Get pagination parameters
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    start = (page - 1) * per_page
    end = start + per_page

    hits, hits_len = get_result(job_id, region, start, end, orderby, asc, dt=True)

    response = {
        "data": hits,
        "draw": int(request.args.get("draw", 1)),
        "recordsTotal": hits_len,
        "recordsFiltered": hits_len,
    }
    return jsonify(response)
