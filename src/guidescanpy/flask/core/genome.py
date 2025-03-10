import os.path
import re
from functools import lru_cache
from collections import OrderedDict, defaultdict
import numpy as np
import pandas as pd
import pysam
import logging
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

logger = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def get_genome_structure(organism, bam_filepath=None):
    return GenomeStructure(organism=organism, bam_filepath=bam_filepath)


class GenomeStructure:
    def __init__(self, organism=None, bam_filepath=None, chr2acc_filepath=None):
        self.organism = organism

        if chr2acc_filepath is None:
            assert (
                organism is not None
            ), "Need to specify organism in constructor to get chr2acc mapping from db"
            self.acc_to_chr = get_chromosome_names(organism)
        else:
            chr2acc = pd.read_csv(chr2acc_filepath, sep="\t")
            assert "#Chromosome" in chr2acc.columns
            assert "Accession.version" in chr2acc.columns
            chr2acc["chr"] = "chr" + chr2acc["#Chromosome"]
            self.acc_to_chr = chr2acc.set_index("Accession.version")["chr"].to_dict()

        self.chr_to_acc = {v: k for k, v in self.acc_to_chr.items()}

        if bam_filepath is None:
            bam_dir = config.guidescan.grna_database_path_prefix
            bam_filename = getattr(
                getattr(config.guidescan.grna_database_path_map, organism), "cas9"
            )
            bam_filepath = os.path.join(bam_dir, bam_filename)

        with pysam.AlignmentFile(bam_filepath, "r") as bam:
            self.acc_to_length = OrderedDict(zip(bam.references, bam.lengths))
            # TODO: The following 2 attributes are not required if we have self.acc_to_length, and can be obsoleted
            self.genome = bam.lengths, bam.references
            self.absolute_genome = np.insert(np.cumsum(bam.lengths), 0, 0)
            self.off_target_delim = -(self.absolute_genome[-1] + 1)

    def _all_regions(self):
        regions = []
        for chr, acc in self.chr_to_acc.items():
            start, end = 1, self.acc_to_length[acc]
            regions.append((f"{chr}:{start}-{end}", chr, start, end))
        return regions

    def parse_regions(
        self, region_string: str | None = None, flanking: int = 0
    ) -> list:
        if region_string is None:
            parser = self._all_regions()
        else:
            parser = region_parser(
                filepath_or_str=region_string, organism=self.organism
            )

        regions = []
        for region_name, chr, start, end in parser:
            region = {
                "region-name": region_name,
                "chromosome-name": chr,
                "coords": (chr, start, end),
            }

            if flanking > 0:
                chromosome_name = region["chromosome-name"]
                _, start_pos, end_pos = region["coords"]
                region_name = region["region-name"]

                _regions = [
                    {
                        "region-name": f"{region_name}:left-flank",
                        "chromosome-name": chromosome_name,
                        "coords": (
                            chromosome_name,
                            max(1, start_pos - flanking),
                            start_pos,
                        ),
                    },
                    {
                        "region-name": f"{region_name}:right-flank",
                        "chromosome-name": chromosome_name,
                        "coords": (
                            chromosome_name,
                            end_pos,
                            min(
                                self.acc_to_length[self.chr_to_acc[chromosome_name]],
                                end_pos + flanking,
                            ),
                        ),
                    },
                ]
                regions.extend(_regions)
            else:
                regions.append(region)

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

    def to_coordinate_string(
        self,
        read=None,
        accession=None,
        start=None,
        end=None,
        direction=None,
        offset=0,
        is_one_indexed=False,
    ):
        if read is None:
            assert all(x is not None for x in (accession, start, end, direction))
            # All subsequent logic assumed incoming 0-indexed position values
            # If they are 1-indexed, then we'll add -1 to them before proceeding
            if is_one_indexed:
                start -= 1
                end -= 1
        else:
            accession = read.reference_name
            direction = "+" if read.is_forward else "-"
            start = read.reference_start
            end = read.reference_end

        chr = self.acc_to_chr[accession]
        # Convert from 0-indexed (start, end] to 1-indexed [start, end]
        # Fix offset for certain databases
        return f"{chr}:{start+1+offset}-{end+offset}:{direction}"

    def off_target_region_string(self, off_target_dict, reference_length):
        position = off_target_dict["position"]
        chromosome = off_target_dict.get("chromosome")

        if chromosome is None:
            assert (
                "accession" in off_target_dict
            ), "If not specifying chromosome, please specify accession"
            chromosome = self.acc_to_chr[off_target_dict["accession"]]
        if not chromosome.startswith("chr"):
            chromosome = "chr" + chromosome

        if off_target_dict["direction"] == "+":
            # For + strand, position denotes the (0-indexed, inclusive) end of the match
            # Convert this to (1-indexed, inclusive)
            end = position + 1
            # The start index (1-indexed, inclusive) is end - len(seq_including_pam) + 1
            start = end - reference_length + 1
        else:
            # For - strand, position denotes the (0-indexed, inclusive) start of the match
            # Convert this to (1-indexed, inclusive)
            start = position + 1
            # The end index (1-indexed, inclusive) is start + len(seq_including_pam) - 1
            end = start + reference_length - 1
        return f"{chromosome}:{start}-{end}"

    def off_targets_from_read(self, read):
        offtarget_hex = read.get_tag("of")
        off_target_tuples = hex_to_offtarget_info(
            offtarget_hex, delim=self.off_target_delim
        )
        total_off_target_tuples = len(
            off_target_tuples
        )  # This will be used to get the number of 0-off-target

        # Remove off-target entries with distance = 0 (should be just the first, but we go through all anyway)
        off_target_tuples = tuple(t for t in off_target_tuples if t[0] != 0)

        off_targets = []
        off_targets_by_distance = defaultdict(int)
        off_targets_by_distance[0] = total_off_target_tuples - len(off_target_tuples)
        for dist, pos in off_target_tuples:
            dist = int(dist)
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
                off_target, read.reference_length
            )
            off_targets.append(off_target)
            off_targets_by_distance[dist] += 1

        return off_targets, off_targets_by_distance

    def query(
        self,
        region,
        enzyme="cas9",
        topn=None,
        min_specificity=None,
        min_ce=None,
        min_gc=None,
        max_gc=None,
        pattern_avoid=None,
        filter_annotated=False,
        as_dataframe=False,
        bam_filepath=None,
        reorder=True,
    ):
        chromosome, start_pos, end_pos = region["coords"]
        if chromosome not in self.chr_to_acc:
            return None
        chromosome = self.chr_to_acc[chromosome]

        if bam_filepath is None:
            bam_dir = config.guidescan.grna_database_path_prefix
            bam_filename = getattr(
                getattr(config.guidescan.grna_database_path_map, self.organism), enzyme
            )
            bam_filepath = os.path.join(bam_dir, bam_filename)

        # Certain legacy .bam files have incorrect POS fields. We maintain an offset
        # to add to any alignment read we get from the .bam file
        if self.organism is not None:
            read_offset = getattr(
                config.guidescan.grna_db_offset_map, self.organism + ":" + enzyme, 0
            )
        else:
            read_offset = 0

        results = []

        with pysam.AlignmentFile(bam_filepath, "r") as bam:
            if not bam.has_index():
                logger.warning("Index not found! Attempting to create index.")
                pysam.index(bam_filepath)

        with pysam.AlignmentFile(bam_filepath, "r") as bam:
            for i, read in enumerate(bam.fetch(chromosome, start_pos, end_pos)):
                annotations = []
                interval_tree = get_chromosome_interval_trees().get(chromosome)

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

                if interval_tree is not None and interval_tree.overlap(this_interval):
                    overlaps = interval_tree[this_interval.begin : this_interval.end]
                    for overlap in overlaps:
                        exon, product = overlap.data
                        annotations.append(f"Exon {exon} of {product}")

                off_targets, off_targets_by_distance = self.off_targets_from_read(read)

                cutting_efficiency = specificity = None
                if read.has_tag("ce"):  # new guidescan BAM format
                    cutting_efficiency = read.get_tag("ce")
                elif read.has_tag("ds"):  # old guidescan BAM format
                    cutting_efficiency = read.get_tag("ds")
                if read.has_tag("sp"):  # new guidescan BAM format
                    specificity = read.get_tag("sp")
                elif read.has_tag("cs"):  # old guidescan BAM format
                    specificity = read.get_tag("cs")

                sequence = read.get_forward_sequence()
                if enzyme == "cas9":
                    sequence_no_pam = sequence[:-3]
                else:
                    sequence_no_pam = sequence[4:]
                gc_content = (
                    sequence_no_pam.count("G") + sequence_no_pam.count("C")
                ) / 20

                result = {
                    "id": read.query_name,
                    "query-sequence": read.query_sequence,
                    "gc-content": gc_content,
                    "reference-name": read.reference_name,
                    "offtargets-by-distance": off_targets_by_distance,
                    "coordinate": self.to_coordinate_string(read, offset=read_offset),
                    "sequence": sequence,
                    "start": read.reference_start
                    + 1
                    + read_offset,  # 0-indexed inclusive -> 1-indexed inclusive
                    "end": read.reference_end
                    + read_offset,  # 0-indexed exclusive -> 1-indexed inclusive
                    "direction": "+" if read.is_forward else "-",
                    "cutting-efficiency": cutting_efficiency,
                    "specificity": specificity,
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
            # Only filter on specificity when enzyme is cas9, since specificity values are NA otherwise
            if min_specificity is not None and enzyme == "cas9":
                results = results[results["specificity"] >= min_specificity]

            # Only filter on cutting efficiency when enzyme is cas9, since specificity values are NA otherwise
            if min_ce is not None and enzyme == "cas9":
                results = results[results["cutting-efficiency"] >= min_ce]

            if min_gc is not None:
                results = results[results["gc-content"] >= min_gc]
            if max_gc is not None:
                results = results[results["gc-content"] <= max_gc]

            if pattern_avoid is not None:
                wildcard_to_nuc = {"N": "ACTG", "V": "ACG"}
                nuc_map = {"A": "T", "T": "A", "C": "G", "G": "C"}
                patterns_avoid = [pattern_avoid]

                # Replace the two wildcards with all possible representations of nucleotides and store them in patterns_avoid
                for wildcard in wildcard_to_nuc:
                    if any(wildcard in pattern for pattern in patterns_avoid):
                        patterns_avoid = [
                            pattern.replace(wildcard, x)
                            for x in wildcard_to_nuc[wildcard]
                            for pattern in patterns_avoid
                            if wildcard in pattern
                        ]

                # Also add the reverse complemented patterns to patterns_avoid
                patterns_avoid.extend(
                    [
                        "".join(list(map(lambda n: nuc_map[n], dna))[::-1])
                        for dna in patterns_avoid
                    ]
                )

                exclude_reg = "|".join(re.escape(pattern) for pattern in patterns_avoid)
                results = results[~results["sequence"].str.contains(exclude_reg)]

            if filter_annotated:
                results = results[results["annotations"] != ""]

            if reorder:
                results = results.sort_values(
                    by=["specificity", "n-off-targets"], ascending=[False, True]
                )

            results = results[:topn]
            results.reset_index(inplace=True, drop=True)

        if as_dataframe:
            return results
        else:
            return results.to_dict("records")
