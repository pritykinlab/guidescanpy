import numpy as np
import binascii
import functools
from flask import render_template
from guidescanpy.tasks import app as tasks_app
from guidescanpy.exceptions import GuidescanException


def repeat(item):
    while True:
        yield item


def get_length(genome):
    return sum(p["LN"] for p in genome)


def get_nonexist_int_coord(genome):
    return -(get_length(genome) + 1)


def ilen(iterable):
    return functools.reduce(lambda sum, _: sum + 1, iterable, 0)


def hex_to_array(hexstr):
    return np.frombuffer(binascii.unhexlify(hexstr), dtype=int)


def hex_to_offtarget_info(hexstr, delim):
    mainarr = hex_to_array(hexstr)
    index = np.where(mainarr == delim)[0]
    slices = list(zip(np.insert(index, 0, -1), index))
    out = []
    for start, end in slices:
        out += zip(repeat(mainarr[end - 1]), mainarr[start + 1 : end - 1])
    return out


def map_int_to_coord(x, genome):
    strand = "+" if x > 0 else "-"
    x = abs(x)
    i = 0
    while genome[i]["LN"] <= x:
        x -= genome[i]["LN"]
        i += 1
    chrom = genome[i]["SN"]
    coord = x

    return chrom, coord, strand


def job_result(view):
    """
    A decorator for Flask view functions that display job results.
    This function determines whether a GuidescanException is raised
    by the job, and if so, intercepts the view function and returns a
    template that displays the error message.
    """

    @functools.wraps(view)
    def wrapped_view(job_id):
        result = tasks_app.AsyncResult(job_id)
        if result.status == "FAILURE" and isinstance(result.result, GuidescanException):
            return render_template("job.html", result=result, error=str(result.result))
        else:
            return view(job_id)

    return wrapped_view
