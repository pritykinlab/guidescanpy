import argparse
import math
import pysam


def get_parser(parser):
    parser.add_argument(
        "--input", "-i", type=str, required=True, help="Path to the input sam/bam file."
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Path to the output sam/bam file.",
    )
    parser.add_argument(
        "--k0",
        type=int,
        default=1,
        help="Max number of off-targets at distance 0 (default=%(default)s)",
    )
    parser.add_argument(
        "--k1",
        type=int,
        default=0,
        help="Max number of off-targets at distance 1 (default=%(default)s)",
    )
    parser.add_argument(
        "--k2",
        type=int,
        default=math.inf,
        help="Max number of off-targets at distance 2 (default=%(default)s)",
    )
    parser.add_argument(
        "--k3",
        type=int,
        default=math.inf,
        help="Max number of off-targets at distance 3 (default=%(default)s)",
    )
    return parser


def main(args):
    parser = argparse.ArgumentParser(
        description="Filter a sam/bam file based on the number of offtargets at a given distance."
    )
    args = get_parser(parser).parse_args(args)

    input_file, output_file = args.input, args.output

    if output_file.endswith(".bam") or output_file.endswith(".bam.sorted"):
        writing_mode = "wb"
    elif output_file.endswith(".sam"):
        writing_mode = "w"
    else:
        print("Unknown output format. Using default format 'bam'.")
        writing_mode = "wb"

    with pysam.AlignmentFile(input_file) as input_file, pysam.AlignmentFile(
        output_file, writing_mode, header=input_file.header
    ) as output_file:
        for read in input_file:
            invalid_read = any(
                read.has_tag(ki) and read.get_tag(ki) > getattr(args, ki)
                for ki in ("k0", "k1", "k2", "k3")
            )
            if not invalid_read:
                output_file.write(read)
