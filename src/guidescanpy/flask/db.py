import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from guidescanpy import config


conn = psycopg2.connect(config.guidescan.db)


def insert_chromosome_query(**kwargs):
    query = "INSERT INTO chromosomes (accession, name, organism) VALUES (%s, %s, %s)"
    cur = conn.cursor()
    cur.execute(query, (kwargs['accession'], kwargs['name'], kwargs['organism']))
    conn.commit()
    cur.close()


def insert_gene_query(**kwargs):
    query = "INSERT INTO genes (entrez_id, gene_symbol, chromosome, sense, start_pos, end_pos) VALUES (%s, %s, %s, %s, %s, %s)"
    cur = conn.cursor()
    cur.execute(query, (kwargs['entrez_id'], kwargs['gene_symbol'], kwargs['chromosome'], kwargs['sense'], kwargs['start_pos'], kwargs['end_pos']))
    conn.commit()
    cur.close()


def insert_exon_query(**kwargs):
    query = "INSERT INTO exons (entrez_id, exon_number, chromosome, product, sense, start_pos, end_pos) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cur = conn.cursor()
    cur.execute(query, (kwargs['entrez_id'], kwargs['exon_number'], kwargs['chromosome'], kwargs['product'], kwargs['sense'], kwargs['start_pos'], kwargs['end_pos']))
    conn.commit()
    cur.close()


def create_region_query(organism, region):
    try:
        int(region)
    except ValueError:
        is_entrez_id = False
    else:
        is_entrez_id = True

    query = "SELECT genes.entrez_id, genes.gene_symbol AS region_name, genes.start_pos AS start_pos, genes.end_pos AS end_pos, " \
            "genes.sense, chromosomes.name AS chromosome_name, chromosomes.accession AS chromosome_accession FROM genes, chromosomes " \
            "WHERE genes.chromosome=chromosomes.accession AND chromosomes.organism = %s"

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
    query = sql.SQL("SELECT accession, CONCAT('chr', name) FROM chromosomes "
                    "WHERE organism = %s")
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query, (organism,))
    result = cur.fetchall()
    if result is not None:
        return dict(result)
    else:
        return None