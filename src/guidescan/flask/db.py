import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from guidescan import config


conn = psycopg2.connect(config.guidescan.db)


def create_gene_symbol_query(gene_symbol, organism):
    # Get chromosome + position data for a gene
    query = sql.SQL("SELECT genes.entrez_id, genes.gene_symbol, genes.start_pos, genes.end_pos, "
                    "genes.sense, chromosomes.name, chromosomes.accession FROM genes, chromosomes "
                    "WHERE genes.gene_symbol = %s AND genes.chromosome=chromosomes.accession AND chromosomes.organism = %s")
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query, (gene_symbol, organism))
    result = cur.fetchone()
    if result is not None:
        return dict(result)
    else:
        return None


def get_chromosome_names(organism):
    query = sql.SQL("SELECT accession, name FROM chromosomes "
                    "WHERE organism = %s")
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query, (organism,))
    result = cur.fetchall()
    if result is not None:
        return dict(result)
    else:
        return None