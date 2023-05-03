import numpy as np
import binascii
from functools import reduce


def repeat(item):
    while True:
        yield item


def get_length(genome):
    return sum(p["LN"] for p in genome)


def get_nonexist_int_coord(genome):
    return -(get_length(genome) + 1)


def ilen(iterable):
    return reduce(lambda sum, _: sum + 1, iterable, 0)


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
