from flask import Flask, redirect, url_for
from guidescanpy import __version__, config


def create_app(debug=False):
    app = Flask(
        "guidescanpy",
        static_url_path="/pystatic",
        static_folder="flask/static",
        template_folder="flask/templates",
    )
    app.config.from_object(config.flask)

    if debug:
        from werkzeug.debug import DebuggedApplication

        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

    from guidescanpy.flask.blueprints import (
        web,
        info,
        query,
        library,
        sequence,
        job_query,
        job_sequence,
        job_library,
        downloads,
    )

    app.register_blueprint(web.bp, url_prefix="/py")
    app.register_blueprint(info.bp, url_prefix="/py/info")
    app.register_blueprint(query.bp, url_prefix="/py/query")
    app.register_blueprint(library.bp, url_prefix="/py/library")
    app.register_blueprint(sequence.bp, url_prefix="/py/sequence")
    app.register_blueprint(job_query.bp, url_prefix="/py/job/query")
    app.register_blueprint(job_sequence.bp, url_prefix="/py/job/sequence")
    app.register_blueprint(job_library.bp, url_prefix="/py/job/library")
    # Served at the root since the Downloads page links to /indices and /databases
    app.register_blueprint(downloads.bp)

    @app.route("/")
    def root():
        return redirect(url_for("web.index"))

    app.add_template_global(lambda: __version__, name="app_version")
    return app
