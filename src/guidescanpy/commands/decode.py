import argparse
from guidescanpy.flask.core.genome import GenomeStructure


def get_parser(parser):
    parser.add_argument(
        "grna_database", help="SAM/BAM file containing Guidescan2 processed gRNAs."
    )
    parser.add_argument(
        "fasta_file", help="FASTA file for resolving off-target sequences."
    )
    parser.add_argument("chr2acc_file", help="chr2acc file for chromosome resolution")
    parser.add_argument(
        "--region", action="append", type=str, help="One or more region strings"
    )

    parser.add_argument(
        "--mode",
        help="Succinct or complete off-target information.",
        choices=["succinct", "complete"],
        default="succinct",
    )

    return parser


def main(args):
    parser = argparse.ArgumentParser(description=__doc__)
    args = get_parser(parser).parse_args(args)

    if not bool(args.region):
        region_string = None
    else:
        region_string = "\r\n".join(args.region)

    genome = GenomeStructure(
        bam_filepath=args.grna_database, chr2acc_filepath=args.chr2acc_file
    )
    regions = genome.parse_regions(region_string=region_string)

    if args.mode == "succinct":
        print(
            "id,sequence,chromosome,position,sense,distance_0_matches,distance_1_matches,distance_2_matches,distance_3_matches,specificity"
        )

        for region in regions:
            results = genome.query(
                region, bam_filepath=args.grna_database, reorder=False
            )
            for i, result in enumerate(results):
                cols = [
                    result["id"],
                    result["sequence"],  # Forward sequence regardless of strand
                    result["reference-name"],
                    result["start"],  # 1-indexed start position
                    result["direction"],
                    result["offtargets-by-distance"][0],
                    result["offtargets-by-distance"][1],
                    result["offtargets-by-distance"][2],
                    result["offtargets-by-distance"][3],
                    result["specificity"],
                ]
                print(",".join(str(col) for col in cols))
    else:
        raise RuntimeError("Not implemented yet")
