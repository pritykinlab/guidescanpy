import os.path
import logging
from guidescanpy.flask.db import get_connection

logger = logging.getLogger(__name__)


def main(_):
    conn = get_connection()
    cur = conn.cursor()

    init_db_script_file = os.path.join(os.path.dirname(__file__), "init_db.sql")
    with open(init_db_script_file) as f:
        init_db_script = f.read()

    cur.execute(init_db_script)
    conn.commit()
    conn.close()

    logger.info("Initialized database.")
