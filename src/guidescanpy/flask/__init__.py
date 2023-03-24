from flask import Flask

from guidescanpy import __version__, config
from guidescanpy.flask.blueprints import cache


def create_app(debug=False):

    app = Flask('guidescanpy', static_folder='flask/static', template_folder='flask/templates')
    app.config.from_object(config.flask)
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

    if debug:
        from werkzeug.debug import DebuggedApplication
        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

    from guidescanpy.flask.blueprints import web, info, query, job

    app.register_blueprint(web.bp, url_prefix='/')
    app.register_blueprint(info.bp, url_prefix='/info')
    app.register_blueprint(query.bp, url_prefix='/query')
    app.register_blueprint(job.bp, url_prefix='/job')

    app.add_template_global(lambda: __version__, name='app_version')
    return app
