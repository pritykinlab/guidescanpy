import logging
from flask import Blueprint, jsonify, render_template, make_response, abort, request
import pandas as pd
from guidescanpy.tasks import app as tasks_app
from guidescanpy.flask.core.utils import job_result


bp = Blueprint("job_query", __name__)
logger = logging.getLogger(__name__)


@bp.route("/<job_id>")
@job_result
def job(job_id):
    result = tasks_app.AsyncResult(job_id)
    if result.status == "SUCCESS":
        # TODO: Is there a cleaner way to do this?
        first_region = (
            list(result.result["queries"].values())[0]["region"]
            if ("queries" in result.result) and result.result["queries"]
            else ""
        )
    else:
        first_region = ""
    return render_template("job_query.html", result=result, first_region=first_region)


@bp.route("/status/<job_id>")
def status(job_id):
    res = tasks_app.AsyncResult(job_id)
    return jsonify({"status": res.status})


def get_result(job_id, region=None, start=0, end=None, orderby=None, asc=True):
    """
    return a full result dictionary for non-DataTable use, a 'hits' dictionary for DataTable use.
    """
    result = tasks_app.AsyncResult(job_id).result

    if region is None:
        regions = result["queries"].keys()
    else:
        assert region in result["queries"], f"Region {region} not found in results"
        regions = [region]

    for region in regions:
        value = result["queries"][region]
        hits = pd.DataFrame(value["hits"])
        total_hits = len(hits)
        if orderby:
            hits.sort_values(by=orderby, ascending=asc, inplace=True)
        hits = hits[start:end]
        hits = hits.to_dict("records")

        result["queries"][region] = {
            "region": value["region"],
            "hits": hits,
            "total_hits": total_hits,
        }

    return result


@bp.route("/result/<format>/<job_id>", defaults={"offtarget": False})
@bp.route("/result/<format>/<offtarget>/<job_id>")
def result(format, job_id, offtarget):
    region = request.args.get("region")
    orderby = request.args.get("orderby")
    asc = request.args.get("asc") == "asc"
    start = int(request.args.get("start", 0))
    end = (
        int(request.args.get("limit")) + start
        if request.args.get("limit") is not None
        else None
    )
    result = get_result(job_id, region, start, end, orderby, asc)

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
            if offtarget:
                lines = [
                    "Region-name,gRNA-ID,gRNA-Seq,Number of off-targets,"
                    "Off-target summary,Off-target accession,Off-target chromosome,"
                    "Off-target direction,Off-target distance,Off-target position,"
                    "Off-target region-string,"
                    "Cutting efficiency,Specificity,GC,Rank,Coordinates,Strand,Annotations"
                ]
            else:
                lines = [
                    "Region-name,gRNA-ID,gRNA-Seq,Number of off-targets,"
                    "Off-target summary,Cutting efficiency,Specificity,GC,Rank,Coordinates,Strand,Annotations"
                ]

            for _, v in result["queries"].items():
                for i, hit in enumerate(v["hits"], start=1):
                    if offtarget:
                        n_off_targets = hit["n-off-targets"]
                        if n_off_targets == 0:
                            hit["off-targets"].append(
                                {
                                    "accession": "",
                                    "chromosome": "",
                                    "direction": "",
                                    "distance": "",
                                    "position": "",
                                    "region-string": "",
                                }
                            )
                        for off_target in range(max(1, n_off_targets)):
                            lines.append(
                                ",".join(
                                    str(x)
                                    for x in [
                                        hit["region-string"],
                                        hit["region-string"] + f".{i}",
                                        hit["sequence"],
                                        hit["n-off-targets"],
                                        hit["off-target-summary"],
                                        hit["off-targets"][off_target]["accession"],
                                        hit["off-targets"][off_target]["chromosome"],
                                        hit["off-targets"][off_target]["direction"],
                                        hit["off-targets"][off_target]["distance"],
                                        hit["off-targets"][off_target]["position"],
                                        hit["off-targets"][off_target]["region-string"],
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
                        if n_off_targets == 0:
                            hit["off-targets"] = []
                    else:
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
    assert (
        region is not None
    ), "DataTables format only supported when region is specified"

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

    result = get_result(job_id, region, start, end, orderby, asc)
    data = result["queries"][region]
    hits, total_hits = data["hits"], data["total_hits"]

    response = {
        "data": hits,
        "draw": int(request.args.get("draw", 1)),
        "recordsTotal": total_hits,
        "recordsFiltered": total_hits,
    }
    return jsonify(response)
