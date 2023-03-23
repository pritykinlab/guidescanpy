import os.path
import re
from functools import lru_cache
from collections import OrderedDict
from typing import Union
import numpy as np
import pandas as pd
import pysam
from guidescanpy.flask.db import get_chromosome_names, create_region_query
from guidescanpy.flask.core.utils import hex_to_offtarget_info
from guidescanpy import config


EMULATE_BUG1 = True
EMULATE_BUG2 = True


@lru_cache(maxsize=32)
def get_genome_structure(organism):
    return GenomeStructure(organism=organism)


class GenomeStructure:
    def __init__(self, organism=None):

        self.organism = organism

        bam_dir = config.guidescan.grna_database_path_prefix
        bam_filename = getattr(getattr(config.guidescan.grna_database_path_map, organism), 'cas9')
        self.acc_to_chr = get_chromosome_names(organism)
        self.chr_to_acc = {v: k for k, v in self.acc_to_chr.items()}

        bam_filepath = os.path.join(bam_dir, bam_filename)
        with pysam.AlignmentFile(bam_filepath, 'r') as bam:
            self.acc_to_length = OrderedDict(zip(bam.references, bam.lengths))
            # TODO: The following 2 attributes are not required if we have self.acc_to_length, and can be obsoleted
            self.genome = bam.lengths, bam.references
            self.absolute_genome = np.insert(np.cumsum(bam.lengths), 0, 0)
            self.off_target_delim = -(self.absolute_genome[-1] + 1)

    def parse_region(self, region: str) -> Union[dict, None]:
        # region can be chr:start-end where start and end are 1-indexed and inclusive
        region = region.replace(',', '')
        match = re.match(r'^(.*):(\d+)-(\d+)', region)
        if match is not None:
            chr, start, end = match.group(1), int(match.group(2)), int(match.group(3))
            if chr not in self.chr_to_acc:
                return None
            else:
                acc = self.chr_to_acc[chr]
                acc_length = self.acc_to_length[acc]
                if start > acc_length or end > acc_length or start > end:
                    return None
                else:
                    retval = {
                        'region-name': region,
                        'chromosome-name': chr,
                        'coords': (acc, start, end)
                    }
        else:
            region = create_region_query(self.organism, region)
            if region is None:
                return None
            retval = {
                'region-name': region['region_name'],
                'chromosome-name': region['chromosome_name'],
                'coords': (region['chromosome_accession'], region['start_pos'], region['end_pos'])
            }
        return retval

    def find_position(self, absolute_coords):
        """
        Find the index of the value in `self.absolute_genome` sorted array using binary search.
        If the value is not found, return the index of the rightmost element whose value is less than the search value.
        """
        # to_genomic_coordinates works well enough for now
        raise NotImplementedError

    def to_genomic_coordinates(self, pos):
        strand = 'positive' if pos > 0 else 'negative'
        if EMULATE_BUG2:
            pos = pos.astype(np.int32)
        x = abs(pos)
        i = 0
        while self.genome[0][i] <= x:
            x -= self.genome[0][i]
            i += 1

        chrom = self.genome[1][i]
        coord = x

        return chrom, coord, strand

    def query(self, region, start_pos=None, end_pos=None, enzyme='cas9'):

        results = []
        if start_pos is None or end_pos is None:
            region = self.parse_region(region)
            if region is None:
                return results
            chromosome, start_pos, end_pos = region['coords']
        else:
            chromosome = region

        bam_dir = config.guidescan.grna_database_path_prefix
        bam_filename = getattr(getattr(config.guidescan.grna_database_path_map, self.organism), enzyme)
        bam_filepath = os.path.join(bam_dir, bam_filename)

        with pysam.AlignmentFile(bam_filepath, 'r') as bam:
            for i, read in enumerate(bam.fetch(chromosome, start_pos, end_pos)):

                offtarget_hex = read.get_tag('of')
                off_target_tuples = hex_to_offtarget_info(offtarget_hex, delim=self.off_target_delim)

                if EMULATE_BUG1:
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

                    # remove 'chr' prefix and return if chr is found, else return None
                    # (if off-target is on a scaffold, for example)
                    chr = self.acc_to_chr[genomic_chrom][3:] if genomic_chrom in self.acc_to_chr else None

                    off_target = {
                        'position': genomic_coord,
                        'chromosome': chr,
                        'direction': genomic_strand,
                        'distance': dist,
                        'accession': genomic_chrom,
                    }
                    off_targets.append(off_target)

                result = {
                    'sequence': read.get_forward_sequence(),
                    'start': read.reference_start + 1,  # 0-indexed inclusive -> 1-indexed inclusive
                    'end': read.reference_end,          # 0-indexed exclusive -> 1-indexed inclusive
                    'direction': 'positive' if read.is_forward else 'negative',
                    'cutting-efficiency': read.get_tag('ds'),
                    'specificity': read.get_tag('cs'),
                    'off-targets': off_targets,
                    'n-off-targets': len(off_targets)
                }

                if result['start'] >= start_pos and result['end'] <= end_pos:
                    results.append(result)

        df = pd.DataFrame(results)
        #df = df.sort_values(by=['n-off-targets'])
        return df