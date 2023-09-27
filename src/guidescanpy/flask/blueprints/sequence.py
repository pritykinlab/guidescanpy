import os.path
import pandas as pd
from flask import Blueprint, redirect, url_for, request
from guidescanpy import config
from guidescanpy.core.guidescan import cmd_enumerate
from guidescanpy.flask.core.genome import GenomeStructure

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

    # TODO: Why is this \r\n and not just \n?
    sequences = args["sequences"].split("\r\n")

    start = False  # match PAM at start instead of at end?
    alt_pam = None
    if enzyme == "cpf1":
        start = True
        pam = "TTTN"
    elif enzyme == "cas9":
        pam = "NGG"
        alt_pam = "NAG"
    else:
        raise RuntimeError(f"Unexpected enzyme {enzyme}")

    mismatches = args.get("mismatches", 4)
    if mismatches > 6:  # would be too computationally expensive!
        raise RuntimeError("Max. mismatches should be <= 6")

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

    results = {}
    for kmer_id, kmer_data in data.groupby("id"):
        first_record = kmer_data.iloc[0]
        position = first_record["match_position"]
        specificity = first_record["specificity"]
        kmer_length = len(first_record["sequence"])

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
            if distance > 0:
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

        results[kmer_id] = {
            "coordinate": coordinate,
            "specificity": specificity,
            "num-off-targets": num_offtargets,
            "off-target-summary": "|".join(
                [f"{d}:{len(offtargets[d])}" for d in offtargets]
            ),
            "off-targets": offtargets,
        }

    return results
