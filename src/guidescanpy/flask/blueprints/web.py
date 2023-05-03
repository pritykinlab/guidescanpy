import logging
from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
)
from guidescanpy.flask.blueprints.query import query_endpoint


bp = Blueprint("web", __name__)
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    return redirect(url_for("web.grna_design"))


@bp.route("/grna_design", methods=["GET", "POST"])
def grna_design():
    if request.method == "POST":
        form = request.form
        form_data = {
            "organism": form["selectOrganism"],
            "enzyme": form["selectEnzyme"],
            "query-text": form["txtCoordinates"],
            "filter-annotated": form.get("checkExonic", "off") == "on",
            "mode": "flanking"
            if form.get("checkFlanking", "off") == "on"
            else "within",
        }

        if form.get("checkFlanking", "off") == "on":
            form_data["flanking"] = int(form["txtFlanking"])

        if form.get("checkTopN", "off") == "on":
            form_data["topn"] = int(form["txtTopN"])

        if request.files["fileCoordinates"].read().decode("utf8"):
            form_data["query-file-upload"] = request.files[
                "fileCoordinates"
            ]  # TODO: What should go here?

        if form.get("checkFilterAboveSpecificity", "off") == "on":
            form_data["s-bounds-l"] = float(form["txtFilterAboveSpecificity"])
            form_data["s-bounds-u"] = 1.0

        if form.get("checkFilterAboveCE", "off") == "on":
            form_data["ce-bounds-l"] = float(form["txtFilterAboveCE"])
            form_data["ce-bounds-u"] = 1.0

        results = query_endpoint(form_data)
        return results

    return render_template("grna_design.html")


@bp.route("/gene_targeting_library")
def gene_targeting_library():
    return render_template("gene_targeting_library.html")


@bp.route("/grna_sequence_search")
def grna_sequence_search():
    return render_template("grna_sequence_search.html")


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/downloads")
def downloads():
    return render_template("downloads.html")


@bp.route("/contact")
def contact():
    return render_template("contact.html")
