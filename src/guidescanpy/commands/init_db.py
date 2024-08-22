import argparse
import logging
from guidescanpy.flask.db import get_engine
from guidescanpy.flask.tables import Base


logger = logging.getLogger(__name__)


def get_parser(parser):
    parser.add_argument(
        "--force", action="store_true", help="Force drop all tables."
    )
    return parser


def main(args):
    parser = argparse.ArgumentParser(description="Initialize guidescan database.")
    args = get_parser(parser).parse_args(args)

    engine = get_engine()
    if args.force:
        logger.info("Drop all tables.")
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    logger.info("Initialized database.")
