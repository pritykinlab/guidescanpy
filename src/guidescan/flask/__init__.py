from flask import Flask

from guidescan import __version__, config
from guidescan.flask.blueprints import cache


def create_app(debug=False):

    app = Flask('guidescan', static_folder='flask/static', template_folder='flask/templates')
    app.config.from_object(config.flask)
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

    if debug:
        from werkzeug.debug import DebuggedApplication
        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

    import guidescan.flask.blueprints.info

    app.register_blueprint(guidescan.flask.blueprints.info.bp, url_prefix='/info')

    app.add_template_global(lambda: __version__, name='app_version')
    return app
