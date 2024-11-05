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
import requests
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

        if form.get("checkFilterGCContent", "off") == "on":
            form_data["gc-bounds-l"] = float(form["txtFilterAboveGCContent"])
            form_data["gc-bounds-u"] = float(form["txtFilterBelowGCContent"])

        if form.get("checkFilterGRNAPattern", "off") == "on":
            form_data["pattern_avoid"] = form["txtFilterGRNAPattern"]

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
        enzyme = form["selectEnzyme"]
        if enzyme == "None":
            enzyme = None

        form_data = {
            "organism": form["selectOrganism"],
            "enzyme": enzyme,
            "mismatches": int(form["selectMismatches"]),
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


@bp.route("/feedback")
def feedback():
    return render_template("feedback.html")


@bp.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    # Validate Google Form configuration
    FORM_ID = os.getenv("FEEDBACK_FORM_ID")
    if not FORM_ID:
        return {"message": "Feedback form not found."}, 500
    FORM_URL = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"

    ENTRY_TYPE = os.getenv("FEEDBACK_ENTRY_TYPE")
    ENTRY_QUERY = os.getenv("FEEDBACK_ENTRY_QUERY")
    ENTRY_OVERALL = os.getenv("FEEDBACK_ENTRY_OVERALL")
    ENTRY_FEATTYPE = os.getenv("FEEDBACK_ENTRY_FEATTYPE")
    ENTRY_DESC = os.getenv("FEEDBACK_ENTRY_DESC")
    ENTRY_ALT = os.getenv("FEEDBACK_ENTRY_ALT")
    ENTRY_EMAIL = os.getenv("FEEDBACK_ENTRY_EMAIL")

    for entry in [
        ENTRY_TYPE,
        ENTRY_QUERY,
        ENTRY_OVERALL,
        ENTRY_FEATTYPE,
        ENTRY_DESC,
        ENTRY_ALT,
        ENTRY_EMAIL,
    ]:
        if not entry:
            return {"message": "Feedback form entries not found."}, 500

    # Required fields
    selectFeedbackType = request.form.get("selectFeedbackType")
    selectFeedbackOverall = request.form.get("selectFeedbackOverall")
    txtDescription = request.form.get("txtDescription")
    # Conditionally required field
    selectFeedbackFeatureType = request.form.get("selectFeedbackFeatureType")

    # Validate required fields
    if not selectFeedbackType or not selectFeedbackOverall or not txtDescription:
        return {"message": "Please fill out all required fields."}, 400
    if selectFeedbackType == "Feature request" and not selectFeedbackFeatureType:
        return {"message": "Please fill out all required fields."}, 400

    # Mapping from form fields to Google Form entry IDs
    data = {
        ENTRY_TYPE: selectFeedbackType,
        ENTRY_QUERY: request.form.get("txtFeedbackQueryId"),
        ENTRY_OVERALL: selectFeedbackOverall,
        ENTRY_FEATTYPE: selectFeedbackFeatureType,
        ENTRY_DESC: txtDescription,
        ENTRY_ALT: request.form.get("txtAlternative"),
        ENTRY_EMAIL: request.form.get("txtFeedbackEmail"),
    }

    # Submit form data
    response = requests.post(FORM_URL, data=data)
    if response.status_code == 200:
        return {"message": "Thank you for your feedback!"}, 200
    else:
        return {
            "message": "There was an error submitting your feedback. Please try again."
        }, 500
