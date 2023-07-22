import sys
import os.path
import pickle
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

    input_file, fasta_file, output_file = sys.argv[1:4]

    with open(os.path.join(this_dir, "saved_models/V3_model_nopos.pickle"), "rb") as f:
        model = pickle.load(f)

    fasta_record_dict = SeqIO.to_dict(SeqIO.parse(fasta_file, "fasta"))
    write_mode = "w" if output_file.endswith("sam") else "wb"

    with open(os.path.join(this_dir, "saved_models/V3_model_nopos.pickle"), "rb") as f:
        model = pickle.load(f)
    with pysam.AlignmentFile(input_file) as input_file, pysam.AlignmentFile(
        output_file, write_mode, header=input_file.header
    ) as output_file:
        for i, read in enumerate(input_file):
            tag_value = compute_rs2(read, fasta_record_dict, model)
            read.set_tag("ce", tag_value)
            output_file.write(read)
