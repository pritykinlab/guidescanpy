import pysam
from guidescanpy.flask.core.utils import hex_to_offtarget_info


def test_bam_header(bam_file):
    bam = pysam.AlignmentFile(bam_file, 'r')
    assert len(bam.references) == 17
    assert bam.references[0:3] == ('NC_001133.9', 'NC_001134.8', 'NC_001135.5')
    assert bam.lengths[0:3] == (230218, 813184, 316620)


def test_bam_view(bam_file):
    bam = pysam.AlignmentFile(bam_file, 'r')
    n_reads = 0
    for read in bam.fetch('NC_001134.8', 1, 813184):
        cutting_efficiency = read.get_tag('ds')
        specificity = read.get_tag('cs')
        offtarget = read.get_tag('of')
        x = hex_to_offtarget_info(offtarget, delim=-12157106)
        n_reads += 1
    assert n_reads == 59757