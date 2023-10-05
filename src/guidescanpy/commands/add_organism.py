import argparse
from collections import defaultdict
import logging
import gzip
from guidescanpy.flask.db import (
    insert_chromosome_query,
    insert_gene_query,
    insert_exon_query,
)

logger = logging.getLogger(__name__)


def insert_chromosome(organism, file, delim="\t"):
    # Support both chr2acc and chromAlias formats, with the following (lower-cased)
    # column mappings from chromosome names to accession names
    mappings = {"chromosome": "accession.version", "ucsc": "refseq"}

    mapping = None  # one of the `mappings` keys
    header = None
    result = []

    for line in open(file).readlines():
        if line.startswith("#"):
            if header is None:
                header = [t.strip().lower() for t in line.lstrip("#").split(delim)]
                for k in mappings:
                    if k in header:
                        mapping = k
                assert mapping is not None, f"No recognizable header found for {file}"
        else:
            assert header is not None, f"No header found for {file}"
            tokens = [t.strip() for t in line.split(delim)]
            row = {k: v for k, v in zip(header, tokens)}

            name, accession = row[mapping], row[mappings[mapping]]
            if name.startswith("chr"):
                name = name[3:]  # remove 'chr' prefix
            if (
                not name or not accession
            ):  # handle blank lines (also, some rows in chromAlias files in the wild have no names/accessions!)
                continue

            insert_chromosome_query(
                name=name,
                accession=accession,
                organism=organism,
            )
            result.append(accession)

    return result


def parse_gtf_line(line, line_no):
    parts = [s.strip() for s in line.split("\t")]
    if len(parts) < 8:
        return None

    chr, source, feature_type, start, end, score, sense, frame = parts[:8]
    start = int(start) if start != "." else None
    end = int(end) if end != "." else None
    score = float(score) if score != "." else None
    sense = sense == "+" if sense != "." else None

    attrs = defaultdict(list)
    if len(parts) > 8:
        attribute_str = parts[8]
        attributes = [s.strip() for s in attribute_str.split(";") if s != ""]
        for attr in attributes:
            attr_parts = attr.split(" ")
            k = attr_parts[0]
            v = " ".join(attr_parts[1:]).replace('"', "")
            attrs[k].append(v)

    return {
        "line_no": line_no,
        "chr": chr,
        "source": source,
        "feature_type": feature_type,
        "start": start,
        "end": end,
        "score": score,
        "sense": sense,
        "frame": frame,
        "attrs": attrs,
    }


def get_attr(result, which, multiple=False, missing_ok=False):
    attrs = result["attrs"]
    if which not in attrs:
        if not missing_ok:
            raise KeyError(
                f"Missing attribute {which}. Annotation line_no={result['line_no']}"
            )
        else:
            return [] if multiple else None

    if not multiple:
        if len(attrs[which]) > 1:
            raise RuntimeError(
                f"Multiple attribute {which}. Annotation line_no={result['line_no']}"
            )
        return attrs[which][0]
    else:
        return attrs[which]


def insert_gene(result, accessions):
    gene = get_attr(result, "gene", missing_ok=True)
    if gene is None:
        return

    gene_synonyms = get_attr(result, "gene_synonym", multiple=True, missing_ok=True)
    genes = [gene] + gene_synonyms

    db_xrefs = get_attr(result, "db_xref", missing_ok=True, multiple=True)
    for db_xref in db_xrefs:
        if db_xref.startswith("GeneID:"):
            if result["chr"] in accessions:
                entrez_id = int(db_xref[len("GeneID:") :])
                for gene in genes:
                    row = {
                        "entrez_id": entrez_id,
                        "chromosome": result["chr"],
                        "start_pos": result["start"],
                        "end_pos": result["end"],
                        "gene_symbol": gene,
                        "sense": "true" if result["sense"] else "false",
                    }
                    insert_gene_query(**row)


def insert_exon(result, accessions):
    product = get_attr(result, "product", multiple=True, missing_ok=True)
    if not product:
        return
    product = product[0]
    exon_number = get_attr(result, "exon_number", multiple=True)[0]
    exon_number = int(exon_number)

    db_xrefs = get_attr(result, "db_xref", missing_ok=True, multiple=True)
    for db_xref in db_xrefs:
        if db_xref.startswith("GeneID:"):
            if result["chr"] in accessions:
                entrez_id = int(db_xref[len("GeneID:") :])
                row = {
                    "entrez_id": entrez_id,
                    "chromosome": result["chr"],
                    "start_pos": result["start"],
                    "end_pos": result["end"],
                    "product": product,
                    "exon_number": exon_number,
                    "sense": "true" if result["sense"] else "false",
                }
                insert_exon_query(**row)


def get_parser(parser):
    parser.add_argument(
        "organism", type=str, help="Organism that needs to be added to the database."
    )

    parser.add_argument("gtf_gz", type=str, help="Raw data: gtf.gz file.")

    parser.add_argument("chr2acc", type=str, help="Raw data: chr2acc file.")
    return parser


def main(args):
    parser = argparse.ArgumentParser(description="Add organisms to database.")
    args = get_parser(parser).parse_args(args)

    organism = args.organism
    gtf_gz = args.gtf_gz
    chr2acc = args.chr2acc

    chromosome_accessions = insert_chromosome(organism, chr2acc)

    # https://stackoverflow.com/questions/845058
    with gzip.open(gtf_gz, "rt") as f:
        num_lines = sum(1 for _ in f)

    with gzip.open(gtf_gz, "rt") as f:
        for i, line in enumerate(f, start=1):
            result = parse_gtf_line(line, line_no=i)

            if result is None:
                continue

            if result["feature_type"] == "gene":
                insert_gene(result, accessions=chromosome_accessions)

            if result["feature_type"] == "exon":
                insert_exon(result, accessions=chromosome_accessions)

            if i % 10_000 == 0:
                logger.info(f"Annotations for {organism} - {i}/{num_lines} completed")
