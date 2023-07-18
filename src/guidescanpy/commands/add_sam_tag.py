import argparse
import pysam

supported_tags = ["ce"]


def get_parser(parser):
    parser.add_argument("input", type=str, help="Path to the input sam/bam file.")

    parser.add_argument(
        "--ce",
        action="store_true",
        help="Add cutting-efficiency tag to the sam/bam file.",
    )

    parser.add_argument("--output", "-o", help="Path to the output sam file.")

    parser.add_argument(
        "--output-format",
        choices=["bam", "sam"],
        help="Specify the output file format: bam or sam",
        default="bam",
    )
    return parser


def add_tag(tag_name, input_sam_file, output_sam_file, is_bam):
    if is_bam:
        writting_mode = "wb"
    else:
        writting_mode = "w"
    with pysam.AlignmentFile(input_sam_file, "r") as input_file, pysam.AlignmentFile(
        output_sam_file, writting_mode, header=input_file.header
    ) as output_file:
        for read in input_file:
            tag_value = get_tag_value(tag_name, read)
            read.set_tag(tag_name, tag_value)
            output_file.write(read)


def get_tag_value(tag_name, read):
    """
    This is the calculation function to generate tag_value. Need 'ce' for now.
    """
    match tag_name:
        case "ce":
            tag_value = 1.0
            """
            cutting-efficiency calculation.
            """
        case _:
            raise ValueError(
                f"Unsupported tag. The tag_name should be in {supported_tags}"
            )
    return tag_value


def main(args):
    parser = argparse.ArgumentParser(description="Add tags to the sam/bam file.")
    args = get_parser(parser).parse_args(args)
    if args.output_format == "bam":
        is_bam = True
    else:
        is_bam = False
    for tag_name in supported_tags:
        if tag_name in args:
            add_tag(tag_name, args.input, args.output, is_bam)
