from flask import Flask

from guidescanpy import __version__, config
from guidescanpy.flask.blueprints import cache


def create_app(debug=False):
    app = Flask(
        "guidescanpy",
        static_url_path="/pystatic",
        static_folder="flask/static",
        template_folder="flask/templates",
    )
    app.config.from_object(config.flask)
    cache.init_app(app, config={"CACHE_TYPE": "simple"})

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
    )

    app.register_blueprint(web.bp, url_prefix="/py")
    app.register_blueprint(info.bp, url_prefix="/py/info")
    app.register_blueprint(query.bp, url_prefix="/py/query")
    app.register_blueprint(library.bp, url_prefix="/py/library")
    app.register_blueprint(sequence.bp, url_prefix="/py/sequence")
    app.register_blueprint(job_query.bp, url_prefix="/py/job/query")
    app.register_blueprint(job_sequence.bp, url_prefix="/py/job/sequence")
    app.register_blueprint(job_library.bp, url_prefix="/py/job/library")

    app.add_template_global(lambda: __version__, name="app_version")
    return app
