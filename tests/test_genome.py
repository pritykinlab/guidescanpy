import os.path
import numpy as np
from guidescan.flask.core.genome import GenomeStructure
from guidescan import config


def test_genome_structure(bam_file):
    genome_structure = GenomeStructure(organism='mm10', enzyme='cas9')

    genome = genome_structure.genome
    assert genome[0][0:3] == (195471971, 169725, 241735)
    assert genome[1][0:3] == ('NC_000067.6', 'NT_166280.1', 'NT_166281.1')
    assert np.allclose(genome_structure.absolute_genome[0:4], [0, 195471971, 195641696, 195883431])
    assert genome_structure.off_target_delim == -2818974549

    # Query for the Rad51 region
    # x = genome_structure.query('NC_000068.7', 119112814, 119136073)

    # manually selected region on chr2 - should give 4 aligned reads from BAM
    results = genome_structure.query('NC_000068.7', 119127007, 119127029)
    import pprint
    pprint.pprint(results[1]['off-targets'])
    assert len(results) == 4

