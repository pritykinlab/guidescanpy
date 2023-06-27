import logging
import os.path
from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
)
from werkzeug.utils import secure_filename
from guidescanpy.flask.blueprints.query import query_endpoint
from guidescanpy.flask.blueprints.sequence import sequence_endpoint
from guidescanpy.flask.blueprints.library import library_endpoint

bp = Blueprint("web", __name__)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    return "." in filename and os.path.splitext(filename)[-1] in (
        ".txt",
        ".bed",
        ".gtf",
        ".gff",
    )


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

        if file := request.files.get("fileCoordinates"):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                form_data["file"] = filepath

        if form.get("checkFilterAboveSpecificity", "off") == "on":
            form_data["s-bounds-l"] = float(form["txtFilterAboveSpecificity"])
            form_data["s-bounds-u"] = 1.0

        if form.get("checkFilterAboveCE", "off") == "on":
            form_data["ce-bounds-l"] = float(form["txtFilterAboveCE"])
            form_data["ce-bounds-u"] = 1.0

        if form.get("checkFilterAboveGCContent", "off") == "on":
            form_data["gc-bounds-l"] = float(form["txtFilterAboveGCContent"])
            form_data["gc-bounds-u"] = 1.0

        results = query_endpoint(form_data)
        return results

    return render_template("grna_design.html")


@bp.route("/gene_targeting_library", methods=["GET", "POST"])
def gene_targeting_library():
    if request.method == "POST":
        form = request.form
        form_data = {
            "organism": form["selectOrganism"],
            "append5": form.get("checkAppend5", "off") == "on",
            "genes": form["txtGenes"],
        }

        if form.get("checkPool", "off") == "on":
            form_data["n_pools"] = int(form["txtPool"])
        if form.get("checkNGuides", "off") == "on":
            form_data["n_guides"] = int(form["txtNGuides"])
        if form.get("checkPEG", "off") == "on":
            form_data["frac_essential"] = float(form["txtPEG"])
        if form.get("checkPCG", "off") == "on":
            form_data["frac_control"] = float(form["txtPCG"])

        results = library_endpoint(form_data)
        return results

    return render_template("gene_targeting_library.html")


@bp.route("/grna_sequence_search", methods=["GET", "POST"])
def grna_sequence_search():
    if request.method == "POST":
        form = request.form
        form_data = {
            "organism": form["selectOrganism"],
            "enzyme": form["selectEnzyme"],
            "sequences": form["txtSequence"],
        }
        results = sequence_endpoint(form_data)
        return results

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
