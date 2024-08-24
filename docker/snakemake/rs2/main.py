import sys
import os.path
import pickle
import logging
import argparse
import multiprocessing
import tempfile
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


def compute_rs2_contig(args):
    input_filename, fasta_dict, contig = args
    output_file = tempfile.NamedTemporaryFile(delete=False)
    output_filename = output_file.name

    with pysam.AlignmentFile(input_filename) as input_file, pysam.AlignmentFile(
        output_filename, write_mode, header=input_file.header
    ) as output_file:
        count = input_file.count(contig=contig)
        reads = input_file.fetch(contig=contig)

        for i, read in enumerate(reads, start=1):
            tag_value = compute_rs2(read, fasta_record_dict, model)
            read.set_tag("ce", tag_value)
            output_file.write(read)

            if i % 1000 == 0:
                with multiprocessing.Lock():
                    logger.info("Processing %s (%d/%d reads)." % (contig, i, count))

    pysam.index(output_filename)
    return output_filename


if __name__ == "__main__":
    logger = logging.getLogger("guidescan2")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [guidescan2] [\033[32m%(levelname)s\033[0m] %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("input_filename", type=str, help="input sam/bam file")
    parser.add_argument("fasta_filename", type=str, help="fasta sequence file")
    parser.add_argument("output_filename", type=str, help="output sam/bam file")
    parser.add_argument("--workers", type=int, default=1, help="number of workers")

    args = parser.parse_args()

    fasta_record_dict = SeqIO.to_dict(SeqIO.parse(args.fasta_filename, "fasta"))
    write_mode = "w" if args.output_filename.endswith("sam") else "wb"

    with open(os.path.join(this_dir, "saved_models/V3_model_nopos.pickle"), "rb") as f:
        model = pickle.load(f)

    with pysam.AlignmentFile(args.input_filename) as input_file:
        header = input_file.header
        stats = input_file.get_index_statistics()
        n_contigs = len(stats)

    workers = args.workers
    if workers < 0:
        workers = multiprocessing.cpu_count() - 1

    pool = multiprocessing.Pool(min(workers, n_contigs))
    compute_rs2_contig_args = zip(
        [args.input_filename] * n_contigs,
        [fasta_record_dict] * n_contigs,
        [stat.contig for stat in stats],
    )
    temp_filenames = pool.map(compute_rs2_contig, compute_rs2_contig_args)

    with pysam.AlignmentFile(
        args.output_filename, write_mode, header=header
    ) as output_file:
        for temp_filename in temp_filenames:
            with pysam.AlignmentFile(temp_filename) as input_file:
                for read in input_file.fetch():
                    output_file.write(read)

    pysam.index(args.output_filename)

    for temp_filename in temp_filenames:
        os.remove(temp_filename)
