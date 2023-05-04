import logging
from flask import Blueprint, jsonify, render_template, make_response, abort
from guidescanpy.tasks import app as tasks_app


bp = Blueprint("job", __name__)
logger = logging.getLogger(__name__)


@bp.route("/<job_id>")
def job(job_id):
    res = tasks_app.AsyncResult(job_id)
    status = res.status
    result = res.result if status == "SUCCESS" else None
    if result is not None and result["queries"]:
        # TODO: Is there a cleaner way to do this?
        first_region = list(result["queries"].values())[0]["region"]
    else:
        first_region = ""
    return render_template(
        "job.html",
        job_id=job_id,
        status=status,
        result=result,
        first_region=first_region,
    )


@bp.route("/status/<job_id>")
def status(job_id):
    res = tasks_app.AsyncResult(job_id)
    return jsonify({"status": res.status})


@bp.route("/result/<format>/<job_id>")
def result(format, job_id):
    assert format in ("json", "bed", "csv")
    res = tasks_app.AsyncResult(job_id)
    result = res.result

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
