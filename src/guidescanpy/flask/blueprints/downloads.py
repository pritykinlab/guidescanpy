import os
from flask import Blueprint, abort, redirect, render_template_string, request, send_from_directory
from werkzeug.security import safe_join
from guidescanpy import config

bp = Blueprint("downloads", __name__)

LISTING_TEMPLATE = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Index of {{ path }}</title></head>
<body>
<h1>Index of {{ path }}</h1>
<ul>
{% if subpath %}<li><a href="../">../</a></li>{% endif %}
{% for name, is_dir in entries %}
<li><a href="{{ name }}{% if is_dir %}/{% endif %}">{{ name }}{% if is_dir %}/{% endif %}</a></li>
{% endfor %}
</ul>
</body>
</html>
"""


def _serve(base_dir, subpath):
    # Unresolved environment variables are left as "{VAR}" by the config
    if not base_dir or base_dir.startswith("{") or not os.path.isdir(base_dir):
        abort(404)

    full_path = safe_join(base_dir, subpath) if subpath else base_dir
    if full_path is None:
        abort(404)

    if os.path.isdir(full_path):
        if not request.path.endswith("/"):
            return redirect(request.path + "/")
        entries = sorted(
            (name, os.path.isdir(os.path.join(full_path, name)))
            for name in os.listdir(full_path)
            if not name.startswith(".")
        )
        return render_template_string(
            LISTING_TEMPLATE,
            path=request.path,
            subpath=subpath,
            entries=entries,
        )

    return send_from_directory(base_dir, subpath)


@bp.route("/indices/", defaults={"subpath": ""})
@bp.route("/indices/<path:subpath>")
def indices(subpath):
    return _serve(config.guidescan.download_indices_path, subpath)


@bp.route("/databases/", defaults={"subpath": ""})
@bp.route("/databases/<path:subpath>")
def databases(subpath):
    return _serve(config.guidescan.download_databases_path, subpath)
