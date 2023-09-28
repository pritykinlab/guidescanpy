import os.path
import pandas as pd
from flask import Blueprint, redirect, url_for, request
from guidescanpy import config
from guidescanpy.core.guidescan import cmd_enumerate
from guidescanpy.flask.core.genome import GenomeStructure
from guidescanpy.exceptions import GuidescanException

bp = Blueprint("sequence", __name__)


@bp.route("", methods=["GET"])
def sequence_endpoint(args={}):
    args = args or request.args
    if config.celery.eager:
        return sequence(args)
    else:
        from guidescanpy.tasks import sequence as f

        result = f.delay(args)
        return redirect(url_for("job_sequence.job", job_id=result.task_id))


def sequence(args):
    organism = args["organism"]
    enzyme = args["enzyme"]
    mismatches = args["mismatches"]
    max_sequences = args.get("max_sequences", 10)
    min_sequence_length = args.get("min_sequence_length", 10)
    max_sequence_length = args.get("max_sequence_length", 30)

    if mismatches > 6:  # would be too computationally expensive!
        raise RuntimeError("Max. mismatches should be <= 6")

    # TODO: Why is this \r\n and not just \n?
    sequences = args["sequences"].split("\r\n")

    if len(sequences) > max_sequences:
        raise GuidescanException(f"Maximimum {max_sequences} sequences allowed.")

    for i, seq in enumerate(sequences):
        if len(seq) < min_sequence_length or len(seq) > max_sequence_length:
            raise GuidescanException(
                f"Sequence {i} is not between {min_sequence_length} and {max_sequence_length} NUCs in length."
            )

    if enzyme is None:
        start, pam, alt_pam = False, "", None  # start arbitrary
    elif enzyme == "cpf1":
        start, pam = True, "TTTN"
    elif enzyme == "cas9":
        start, pam, alt_pam = False, "NGG", "NAG"
    else:
        raise RuntimeError(f"Unexpected enzyme {enzyme}")

    index_dir = config.guidescan.index_files_path_prefix
    index_prefix = getattr(config.guidescan.index_files_path_map, organism)
    index_prefix = os.path.join(index_dir, index_prefix)

    data = cmd_enumerate(
        kmers=sequences,
        pam=pam,
        index_filepath_prefix=index_prefix,
        start=start,
        alt_pam=alt_pam,
        mismatches=mismatches,
    )

    genome_structure = GenomeStructure(organism=organism)

    matches = {}
    for kmer_id, kmer_data in data.groupby("id"):
        first_record = kmer_data.iloc[0]
        position = first_record["match_position"]
        specificity = first_record["specificity"]
        sequence = first_record["sequence"]
        kmer_length = len(sequence)

        if pd.isna(position):  # no matches, no mismatches
            coordinate = "NA"
        else:
            accession = first_record["match_chrm"]
            direction = first_record["match_strand"]
            start = position
            end = start + kmer_length  # end is always > start regardless of strand
            coordinate = genome_structure.to_coordinate_string(
                accession=accession,
                start=start,
                end=end,
                direction=direction,
                is_one_indexed=True,
            )

        offtargets = {distance: [] for distance in range(0, mismatches + 1)}
        num_offtargets = 0
        for distance, distance_data in kmer_data.groupby("match_distance"):
            for _, row in distance_data.iterrows():
                match_accession = row["match_chrm"]
                match_chromosome = genome_structure.acc_to_chr.get(match_accession)
                if match_chromosome is None:
                    continue  # ignore offtargets on scaffolds etc.

                num_offtargets += 1
                match_strand = row["match_strand"]
                # Note: The CSV 'position' is always the lower-in-value 1-indexed left position,
                # regardless of strand
                match_start = row["match_position"]
                match_end = match_start + kmer_length - 1
                off_target = {
                    "position": match_start,
                    "direction": match_strand,
                    "distance": distance,
                    "accession": match_accession,
                    "coordinate": f"{match_chromosome}:{match_start}-{match_end}:{match_strand}",
                }
                offtargets[distance].append(off_target)

        matches[kmer_id] = {
            "coordinate": coordinate,
            "specificity": specificity,
            "sequence": sequence,
            "num-exact-matches": len(offtargets[0]),
            "num-inexact-matches": num_offtargets - len(offtargets[0]),
            "num-off-targets": num_offtargets,
            "off-target-summary": " | ".join(
                [f"{d}:{len(offtargets[d])}" for d in offtargets]
            ),
            "off-targets": offtargets,
        }

    results = {"organism": organism, "matches": matches}
    return results
