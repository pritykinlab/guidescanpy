import pysam
from guidescanpy.flask.core.utils import hex_to_offtarget_info


def test_bam_header(bam_file):
    bam = pysam.AlignmentFile(bam_file, 'r')
    assert len(bam.references) == 239
    assert bam.references[0:3] == ('NC_000067.6', 'NT_166280.1', 'NT_166281.1')
    assert bam.lengths[0:3] == (195471971, 169725, 241735)


def test_bam_view(bam_file):
    bam = pysam.AlignmentFile(bam_file, 'r')
    n_reads = 0
    for read in bam.fetch('NC_000068.7', 119112814, 119136073):
        cutting_efficiency = read.get_tag('ds')
        specificity = read.get_tag('cs')
        offtarget = read.get_tag('of')
        x = hex_to_offtarget_info(offtarget, delim=-2818974549)
        n_reads += 1
    assert n_reads == 1434