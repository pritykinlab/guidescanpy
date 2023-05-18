from intervaltree import IntervalTree
from functools import cache
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor, RealDictCursor
from guidescanpy import config

conn = psycopg2.connect(config.guidescan.db)


def insert_chromosome_query(**kwargs):
    query = "INSERT INTO chromosomes (accession, name, organism) VALUES (%s, %s, %s)"
    cur = conn.cursor()
    cur.execute(query, (kwargs["accession"], kwargs["name"], kwargs["organism"]))
    conn.commit()
    cur.close()


def insert_gene_query(**kwargs):
    query = "INSERT INTO genes (entrez_id, gene_symbol, chromosome, sense, start_pos, end_pos) VALUES (%s, %s, %s, %s, %s, %s)"
    cur = conn.cursor()
    cur.execute(
        query,
        (
            kwargs["entrez_id"],
            kwargs["gene_symbol"],
            kwargs["chromosome"],
            kwargs["sense"],
            kwargs["start_pos"],
            kwargs["end_pos"],
        ),
    )
    conn.commit()
    cur.close()


def insert_exon_query(**kwargs):
    query = "INSERT INTO exons (entrez_id, exon_number, chromosome, product, sense, start_pos, end_pos) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cur = conn.cursor()
    cur.execute(
        query,
        (
            kwargs["entrez_id"],
            kwargs["exon_number"],
            kwargs["chromosome"],
            kwargs["product"],
            kwargs["sense"],
            kwargs["start_pos"],
            kwargs["end_pos"],
        ),
    )
    conn.commit()
    cur.close()


def create_region_query(organism, region):
    try:
        int(region)
    except ValueError:
        is_entrez_id = False
    else:
        is_entrez_id = True

    query = (
        "SELECT genes.entrez_id, genes.gene_symbol AS region_name, genes.start_pos AS start_pos, genes.end_pos AS end_pos, "
        "genes.sense, 'chr' || chromosomes.name AS chromosome_name, chromosomes.accession AS chromosome_accession FROM genes, chromosomes "
        "WHERE genes.chromosome=chromosomes.accession AND chromosomes.organism = %s"
    )

    if is_entrez_id:
        query += " AND genes.entrez_id=%s"
    else:
        query += " AND genes.gene_symbol=%s"

    query = sql.SQL(query)
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query, (organism, region))
    result = cur.fetchone()
    if result is not None:
        return dict(result)
    else:
        return None


def get_chromosome_names(organism):
    query = sql.SQL(
        "SELECT accession, CONCAT('chr', name) FROM chromosomes " "WHERE organism = %s"
    )
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query, (organism,))
    result = cur.fetchall()
    if result is not None:
        return dict(result)
    else:
        return None


def get_library_info_by_gene(organism, genes, n_guides=6):
    # TODO: Do we need an ORDER BY here?
    #   See https://github.com/pritykinlab/guidescan-web/blob/master/src/guidescan_web/query/library_design.clj#L150
    query = sql.SQL(
        "SELECT * FROM libraries WHERE organism = %s AND gene_symbol IN (SELECT gene_symbol FROM genes WHERE entrez_id IN (SELECT entrez_id FROM genes WHERE gene_symbol = %s)) LIMIT %s"
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)

    return_value = {}
    for gene in genes:
        return_value[gene] = []
        cur.execute(query, (organism, gene, n_guides))
        results = cur.fetchall()
        for row in results:
            return_value[gene].append(dict(row))

    return return_value


def get_essential_genes(organism, n=1):
    query = sql.SQL(
        "SELECT gene_symbol FROM essential_genes WHERE organism = %s LIMIT %s"
    )
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query, (organism, n))
    result = cur.fetchall()
    return [r[0] for r in result]  # TODO: Ugly!


def get_control_guides(organism, n=1):
    # TODO: Order by?
    query = sql.SQL(
        "SELECT * FROM libraries WHERE organism = %s AND (grna_type='safe_targeting_control' OR grna_type='non_targeting_control') LIMIT %s"
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, (organism, n))
    result = cur.fetchall()
    return [dict(row) for row in result]


@cache
def get_chromosome_interval_trees():
    query = sql.SQL(
        "SELECT chromosome, start_pos, end_pos, exon_number, product FROM exons"
    )
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query)
    result = cur.fetchall()

    chromosomes = {}
    for chr, start, end, exon_number, product in result:
        if chr not in chromosomes:
            chromosomes[chr] = IntervalTree()
        # Convert 1-indexed [start, end] to 0-indexed [start, end)
        chromosomes[chr][start - 1 : end] = exon_number, product

    return chromosomes
