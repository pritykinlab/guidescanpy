import sys
import os.path
import pickle
import logging
import argparse
import pysam
from Bio import SeqIO


this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_dir, "analysis"))
import model_comparison


def revcom(s):
    basecomp = {"A": "T", "C": "G", "G": "C", "T": "A", "U": "A", "N": "N"}
    letters = list(s[::-1])
    letters = [basecomp[base] for base in letters]
    return "".join(letters)


def map_coord_to_30nt_context(fasta_record_dict, chr, start, end, antisense):
    if not antisense:
        pos_start = start - 4
        pos_end = end + 3
        return fasta_record_dict[chr].seq[pos_start:pos_end].upper()
    else:
        pos_start = start - 3
        pos_end = end + 4
        return revcom(fasta_record_dict[chr].seq[pos_start:pos_end].upper())


def compute_rs2(guide_record, fasta_record_dict, model):
    chr, start, end, antisense = (
        guide_record.reference_name,
        guide_record.reference_start,
        guide_record.reference_end,
        guide_record.is_reverse,
    )
    seq = map_coord_to_30nt_context(fasta_record_dict, chr, start, end, antisense)
    seq = "".join([nuc if nuc != "N" else "A" for nuc in list(seq)])

    if len(seq) != 30:
        return 0

    return model_comparison.predict(seq, -1, -1, model)


if __name__ == "__main__":

    logger = logging.getLogger("guidescan2")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [guidescan2] [\033[32m%(levelname)s\033[0m] %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('input_filename', type=str, help='input sam/bam file')
    parser.add_argument('fasta_filename', type=str, help='fasta sequence file')
    parser.add_argument('output_filename', type=str, help='output sam/bam file')
    parser.add_argument('--contig', type=str, help='reference_name of the genomic region (chromosome)')
    parser.add_argument('--start', type=int, default=1, help='start of the genomic region (1-based inclusive)')
    parser.add_argument('--end', type=int, help='end of the genomic region (1-based inclusive)')

    args = parser.parse_args()

    fasta_record_dict = SeqIO.to_dict(SeqIO.parse(args.fasta_filename, "fasta"))
    write_mode = "w" if args.output_filename.endswith("sam") else "wb"

    with open(os.path.join(this_dir, "saved_models/V3_model_nopos.pickle"), "rb") as f:
        model = pickle.load(f)

    start = args.start - 1  # 1-indexed inclusive -> 0-indexed inclusive
    end = args.end          # 1-indexed inclusive -> 0-indexed exclusive

    with pysam.AlignmentFile(args.input_filename) as input_file:
        n_reads = input_file.count(contig=args.contig, start=start, end=end)

    with pysam.AlignmentFile(args.input_filename) as input_file, pysam.AlignmentFile(
        args.output_filename, write_mode, header=input_file.header
    ) as output_file:

        reads = input_file.fetch(contig=args.contig, start=start, end=end)

        for i, read in enumerate(reads, start=1):
            tag_value = compute_rs2(read, fasta_record_dict, model)
            read.set_tag("ce", tag_value)
            output_file.write(read)

            if i % 100 == 0:
                logger.info("Processed %d/%d records" % (i, n_reads))
