"""
A module to define custom Exception classes for Guidescanpy.
"""


class GuidescanException(Exception):
    """
    Catch-all Exception class for all kinds of Guidescan errors.
    Exceptions of this class raised during Celery job execution are not considered programming errors
    (and thus no traceback is reported in the web interface)
    """

    pass
