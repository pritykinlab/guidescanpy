import argparse
import pysam
from guidescanpy.flask.core.genome import GenomeStructure


supported_tags = ("ce",)


def get_parser(parser):
    parser.add_argument(
        "tags",
        nargs="+",
        choices=supported_tags,
        help="List of tags to add.",
    )
    parser.add_argument(
        "--input", "-i", type=str, required=True, help="Path to the input sam/bam file."
    )
    parser.add_argument(
        "--chr2acc", type=str, default=None, help="Path to chr2acc file."
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Path to the output sam/bam file.",
    )
    return parser


def add_tag(tag_name, input_file, output_file, genome_structure=None):
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
            tag_value = get_tag_value(tag_name, read, genome_structure)
            read.set_tag(tag_name, tag_value)
            output_file.write(read)


def get_tag_value(tag_name, read, genome_structure):
    """
    This is the calculation function to generate tag_value. Need 'ce' for now.
    """

    match tag_name:
        case "ce":
            tag_value = get_tag_value_ce(read, genome_structure)
        case _:
            raise ValueError(
                f"Unsupported tag. The tag_name should be in {supported_tags}"
            )
    return tag_value


def get_tag_value_ce(read, genome_structure):
    off_targets, off_targets_by_distance = genome_structure.off_targets_from_read(read)

    # TODO: We have all off-targets in the off_targets variable,
    # as well as summary information in off_targets_by_distance
    # Do something useful with this information!

    return 1.0


def main(args):
    parser = argparse.ArgumentParser(description="Add tags to the sam/bam file.")
    args = get_parser(parser).parse_args(args)

    if args.chr2acc is not None:
        # We have all the information to create a GenomeStructure object
        genome_structure = GenomeStructure(
            bam_filepath=args.input, chr2acc_filepath=args.chr2acc
        )
    else:
        genome_structure = None

    for tag_name in args.tags:
        add_tag(
            tag_name=tag_name,
            input_file=args.input,
            output_file=args.output,
            genome_structure=genome_structure,
        )
