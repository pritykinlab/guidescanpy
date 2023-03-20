import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from guidescan import config


conn = psycopg2.connect(config.guidescan.db)


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