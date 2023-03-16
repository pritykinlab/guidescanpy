import os.path
import numpy as np
import pysam
from guidescan.flask.db import get_chromosome_names
from guidescan.flask.core.utils import hex_to_offtarget_info
from guidescan import config


EMULATE_BUG = True


class GenomeStructure:
    def __init__(self, organism=None, enzyme=None, bam_file=None):

        if bam_file is None:
            assert organism is not None
            assert enzyme is not None
            bam_dir = config.guidescan.grna_database_path_prefix
            bam_filename = config.guidescan.grna_database_path_map.mm10.cas9
            bam_file = os.path.join(bam_dir, bam_filename)
            self.chromosome_names = get_chromosome_names(organism)
        else:
            assert organism is None
            assert enzyme is None
            self.chromosome_names = {}

        self.bam_file = bam_file
        with pysam.AlignmentFile(bam_file, 'r') as bam:
            self.genome = bam.lengths, bam.references
            self.absolute_genome = np.insert(np.cumsum(bam.lengths), 0, 0)
            self.off_target_delim = -(self.absolute_genome[-1] + 1)

    def find_position(self, absolute_coords):
        """
        Find the index of the value in `self.absolute_genome` sorted array using binary search.
        If the value is not found, return the index of the rightmost element whose value is less than the search value.
        """
        # to_genomic_coordinates works well enough for now
        raise NotImplementedError

    def to_genomic_coordinates(self, pos):
        strand = 'positive' if pos > 0 else 'negative'
        x = abs(pos)
        i = 0
        while self.genome[0][i] <= x:
            x -= self.genome[0][i]
            i += 1

        chrom = self.genome[1][i]
        coord = x

        return chrom, coord, strand

    def query(self, chromosome, start_pos, end_pos):
        results = []
        with pysam.AlignmentFile(self.bam_file, 'r') as bam:
            for i, read in enumerate(bam.fetch(chromosome, start_pos, end_pos)):

                offtarget_hex = read.get_tag('of')
                off_target_tuples = hex_to_offtarget_info(offtarget_hex, delim=self.off_target_delim)

                if EMULATE_BUG:
                    current_dist = None
                    new_off_target_tuples = []
                    for off_target_tuple in off_target_tuples:
                        dist = off_target_tuple[0]
                        # skip every 0th entry everytime we encounter a new distance
                        if dist != current_dist:
                            current_dist = dist
                            continue
                        new_off_target_tuples.append(off_target_tuple)
                    off_target_tuples = new_off_target_tuples

                off_targets = []
                for (dist, pos) in off_target_tuples:
                    genomic_chrom, genomic_coord, genomic_strand = self.to_genomic_coordinates(pos)

                    off_target = {
                        'original_pos': pos,
                        'accession': genomic_chrom,
                        'chromosome': self.chromosome_names.get(genomic_chrom, genomic_chrom),
                        'direction': genomic_strand,
                        'distance': dist,
                        'position': genomic_coord
                    }
                    off_targets.append(off_target)

                result = {
                    'sequence': read.seq,
                    'start': read.reference_start + 1,  # 0-indexed inclusive -> 1-indexed inclusive
                    'end': read.reference_end,          # 0-indexed exclusive -> 1-indexed inclusive
                    'direction': 'positive' if read.is_forward else 'negative',
                    'cutting-efficiency': read.get_tag('ds'),
                    'specificity': read.get_tag('cs'),
                    'off-targets': off_targets
                }

                results.append(result)

        return results