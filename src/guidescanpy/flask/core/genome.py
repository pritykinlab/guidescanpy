import os.path
from functools import lru_cache
from collections import OrderedDict, defaultdict
import numpy as np
import pandas as pd
import pysam
from intervaltree import Interval
from guidescanpy.flask.db import (
    get_chromosome_names,
    get_chromosome_interval_trees,
)
from guidescanpy.flask.core.utils import hex_to_offtarget_info
from guidescanpy.flask.core.parser import region_parser
from guidescanpy import config


# Backward compatibility with
#   https://github.com/pritykinlab/guidescan-web/blob/f22066ac15dbb42ad1ee6cad2cfdc553518f6ae9/src/guidescan_web/query/process.clj#L58
ANNOTATION_MAGIC = True


@lru_cache(maxsize=32)
def get_genome_structure(organism):
    return GenomeStructure(organism=organism)


class GenomeStructure:
    def __init__(self, organism=None):
        self.organism = organism

        bam_dir = config.guidescan.grna_database_path_prefix
        bam_filename = getattr(
            getattr(config.guidescan.grna_database_path_map, organism), "cas9"
        )
        self.acc_to_chr = get_chromosome_names(organism)
        self.chr_to_acc = {v: k for k, v in self.acc_to_chr.items()}

        bam_filepath = os.path.join(bam_dir, bam_filename)
        with pysam.AlignmentFile(bam_filepath, "r") as bam:
            self.acc_to_length = OrderedDict(zip(bam.references, bam.lengths))
            # TODO: The following 2 attributes are not required if we have self.acc_to_length, and can be obsoleted
            self.genome = bam.lengths, bam.references
            self.absolute_genome = np.insert(np.cumsum(bam.lengths), 0, 0)
            self.off_target_delim = -(self.absolute_genome[-1] + 1)

    def parse_regions(self, region_string: str, flanking: int = 0) -> list:
        parser = region_parser(filepath_or_str=region_string, organism=self.organism)
        for region_name, chr, start, end in parser:
            region = {
                "region-name": region_name,
                "chromosome-name": chr,
                "coords": (chr, start, end),
            }

            if flanking > 0:
                chromosome_name = region["chromosome-name"]
                chromosome_acc, start_pos, end_pos = region["coords"]
                region_name = region["region-name"]

                regions = [
                    {
                        "region-name": f"{region_name}:left-flank",
                        "chromosome-name": chromosome_name,
                        "coords": (
                            chromosome_acc,
                            max(1, start_pos - flanking),
                            start_pos,
                        ),
                    },
                    {
                        "region-name": f"{region_name}:right-flank",
                        "chromosome-name": chromosome_name,
                        "coords": (
                            chromosome_acc,
                            end_pos,
                            min(self.acc_to_length[chromosome_acc], end_pos + flanking),
                        ),
                    },
                ]
            else:
                regions = [region]

        return regions

    def find_position(self, absolute_coords):
        """
        Find the index of the value in `self.absolute_genome` sorted array using binary search.
        If the value is not found, return the index of the rightmost element whose value is less than the search value.
        """
        # to_genomic_coordinates works well enough for now
        raise NotImplementedError

    def to_genomic_coordinates(self, pos):
        strand = "+" if pos > 0 else "-"
        x = abs(pos)
        i = 0
        while self.genome[0][i] <= x:
            x -= self.genome[0][i]
            i += 1

        chrom = self.genome[1][i]
        coord = x

        return chrom, coord, strand

    def to_coordinate_string(self, read):
        direction = "+" if read.is_forward else "-"
        chr = self.acc_to_chr[read.reference_name]
        # Convert from 0-indexed (start, end] to 1-indexed [start, end]
        return f"{chr}:{read.reference_start+1}-{read.reference_end}:{direction}"

    def off_target_region_string(self, off_target_dict):
        chr = "chr" + off_target_dict["chromosome"]
        # TODO: Just decide on '+' or 'positive' throughout!
        # TODO: Get rid of the magic 22 here
        if off_target_dict["direction"] == "+":
            # For + strand, position denotes the (0-indexed, inclusive) end of the match
            # Convert this to (1-indexed, inclusive)
            end = off_target_dict["position"] + 1
            # The start index (1-indexed, inclusive) is end - len(seq_including_pam) + 1
            start = end - 22
        else:
            # For - strand, position denotes the (0-indexed, inclusive) start of the match
            # Convert this to (1-indexed, inclusive)
            start = off_target_dict["position"] + 1
            end = start + 22
        return f"{chr}:{start}-{end}"

    def query(
        self,
        region,
        enzyme="cas9",
        topn=None,
        min_specificity=None,
        min_ce=None,
        filter_annotated=False,
        as_dataframe=False,
        legacy_ordering=False,
    ):
        chromosome, start_pos, end_pos = region["coords"]
        if chromosome not in self.chr_to_acc:
            return None
        chromosome = self.chr_to_acc[chromosome]

        bam_dir = config.guidescan.grna_database_path_prefix
        bam_filename = getattr(
            getattr(config.guidescan.grna_database_path_map, self.organism), enzyme
        )
        bam_filepath = os.path.join(bam_dir, bam_filename)

        results = []
        with pysam.AlignmentFile(bam_filepath, "r") as bam:
            for i, read in enumerate(bam.fetch(chromosome, start_pos, end_pos)):
                annotations = []
                interval_tree = get_chromosome_interval_trees()[chromosome]

                this_interval = Interval(read.reference_start - 1, read.reference_end)
                if ANNOTATION_MAGIC:
                    cut_offset = 6
                    if read.is_forward:
                        this_interval = Interval(
                            read.reference_end - cut_offset - 1,
                            read.reference_end - cut_offset,
                        )
                    else:
                        this_interval = Interval(
                            read.reference_start + cut_offset,
                            read.reference_start + cut_offset + 1,
                        )

                if interval_tree.overlap(this_interval):
                    overlaps = interval_tree[this_interval.begin : this_interval.end]
                    for overlap in overlaps:
                        exon, product = overlap.data
                        annotations.append(f"Exon {exon} of {product}")

                offtarget_hex = read.get_tag("of")
                off_target_tuples = hex_to_offtarget_info(
                    offtarget_hex, delim=self.off_target_delim
                )

                # Remove off-target entries with distance = 0 (should be just the first, but we go through all anyway)
                off_target_tuples = tuple(t for t in off_target_tuples if t[0] != 0)

                off_targets = []
                off_targets_by_distance = defaultdict(int)
                for dist, pos in off_target_tuples:
                    dist = int(dist)  # TODO: Do we need this?
                    (
                        genomic_chrom,
                        genomic_coord,
                        genomic_strand,
                    ) = self.to_genomic_coordinates(pos)

                    # If the off-target is on a contig/scaffold, ignore it
                    if genomic_chrom not in self.acc_to_chr:
                        continue

                    # remove 'chr' prefix
                    chr = (
                        self.acc_to_chr[genomic_chrom][3:]
                        if genomic_chrom in self.acc_to_chr
                        else None
                    )

                    off_target = {
                        "position": int(genomic_coord),
                        "chromosome": chr,
                        "direction": genomic_strand,
                        "distance": dist,
                        "accession": genomic_chrom,
                    }
                    off_target["region-string"] = self.off_target_region_string(
                        off_target
                    )
                    off_targets.append(off_target)
                    off_targets_by_distance[dist] += 1

                result = {
                    "coordinate": self.to_coordinate_string(read),
                    "sequence": read.get_forward_sequence(),
                    "start": read.reference_start
                    + 1,  # 0-indexed inclusive -> 1-indexed inclusive
                    "end": read.reference_end,  # 0-indexed exclusive -> 1-indexed inclusive
                    "direction": "+" if read.is_forward else "-",
                    "cutting-efficiency": read.get_tag("ds"),
                    "specificity": read.get_tag("cs"),
                    "off-targets": off_targets,
                    "off-target-summary": f"2:{off_targets_by_distance[2]}|3:{off_targets_by_distance[3]}",
                    "n-off-targets": len(off_targets),
                    "annotations": ";".join(annotations),
                }

                if result["start"] >= start_pos and result["end"] <= end_pos:
                    results.append(result)

        results = pd.DataFrame(results)
        results[
            "region-string"
        ] = f"{self.acc_to_chr[chromosome]}:{start_pos}-{end_pos}"

        if not results.empty:
            if min_specificity is not None:
                results = results[results["specificity"] >= min_specificity]

            if min_ce is not None:
                results = results[results["cutting-efficiency"] >= min_ce]

            if filter_annotated:
                results = results[results["annotations"] != ""]

            if legacy_ordering:
                # legacy ordering only for unit testing purposes
                # orders by n-off-targets, otherwise keeps the original order
                results = results.rename_axis("iloc").sort_values(
                    by=["n-off-targets", "iloc"], ascending=[True, True]
                )
            else:
                results = results.sort_values(
                    by=["specificity", "n-off-targets"], ascending=[False, True]
                )

            results = results[:topn]
            results.reset_index(inplace=True, drop=True)

        if as_dataframe:
            return results
        else:
            return results.to_dict("records")
