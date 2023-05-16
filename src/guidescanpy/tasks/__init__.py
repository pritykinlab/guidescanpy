import time
from celery import Celery
from guidescanpy import config


app = Celery("tasks", broker=config.celery.broker, backend=config.celery.backend)


@app.task
def sleep(t):
    time.sleep(int(t))
    return int(t) + 1


@app.task
def query(*args, **kwargs):
    from guidescanpy.flask.blueprints.query import query

    return query(*args, **kwargs)


@app.task
def sequence(*args, **kwargs):
    from guidescanpy.flask.blueprints.sequence import sequence

    return sequence(*args, **kwargs)


@app.task
def library(*args, **kwargs):
    from guidescanpy.flask.blueprints.library import library

    return library(*args, **kwargs)
