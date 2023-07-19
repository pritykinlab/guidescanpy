import argparse
import pysam
import os.path

supported_tags = ["ce"]
supported_formats = ["sam", "bam"]


def get_parser(parser):
    parser.add_argument(
        "tags",
        nargs="+",
        choices=supported_tags,
        help="List of tags to add.",
    )
    parser.add_argument(
        "--input", "-i", type=str, help="Path to the input sam/bam file."
    )
    parser.add_argument(
        "--output", "-o", type=str, help="Path to the output sam/bam file."
    )
    return parser


def add_tag(tag_name, input_file, output_file):
    output_format = get_format(output_file)

    if output_format == "bam":
        writing_mode = "wb"
    elif output_format == "unknown":
        print("Unknown output format. Using default format 'bam'.")
        writing_mode = "wb"
    else:
        writing_mode = "w"

    with pysam.AlignmentFile(input_file) as input_file, pysam.AlignmentFile(
        output_file, writing_mode, header=input_file.header
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


def get_format(file):
    while True:
        file, extension = os.path.splitext(file)
        if len(extension) == 0:
            break
        if extension[1:] in supported_formats:
            return extension[1:]
    return "unknown"


def main(args):
    parser = argparse.ArgumentParser(description="Add tags to the sam/bam file.")
    args = get_parser(parser).parse_args(args)

    for tag_name in args.tags:
        add_tag(tag_name, args.input, args.output)
