# celery worker
# cd /path/to/git/clone/folder
# set FORKED_BY_MULTIPROCESSING=1
# celery -A guidescan.tasks.app worker -l info
#


from celery import Celery
from guidescan import config

app = Celery()
app.config_from_object(config.celery)


@app.task
def grna_query(x):
    import time
    time.sleep(int(x))
    return int(x) + 1
