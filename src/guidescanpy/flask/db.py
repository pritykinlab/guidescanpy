import logging
import os.path
from intervaltree import IntervalTree
from functools import cache
from psycopg2 import sql, OperationalError, errorcodes
from psycopg2.errors import IntegrityError
from psycopg2.extras import DictCursor, RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from guidescanpy import config

engine = None
conn = None
logger = logging.getLogger(__name__)


def get_engine():
    global engine
    if engine is None:
        db = config.guidescan.db
        if db.startswith("sqlite:///"):
            db_path = db[len("sqlite:///") :]
            # resolve db_path relative to this file
            db_path = os.path.join(os.path.dirname(__file__), db_path)
            logger.info(f"{db_path=}")
            db = f"sqlite:///{db_path}"
        engine = create_engine(db)
    return engine


def get_connection():
    global conn
    if conn is None:
        try:
            conn = get_engine().connect()
        except OperationalError as e:
            logger.error(str(e))
    return conn


def insert_chromosome_query(**kwargs):
    conn = get_connection()
    query = text("INSERT INTO chromosomes (accession, name, organism) VALUES (:accession, :name, :organism)")
    try:
        conn.execute(query, kwargs)
        conn.commit()
    except IntegrityError:
        conn.rollback()


def insert_gene_query(**kwargs):
    conn = get_connection()
    query = text("INSERT INTO genes (entrez_id, gene_symbol, chromosome, sense, start_pos, end_pos) VALUES (:entrez_id, :gene_symbol, :chromosome, :sense, :start_pos, :end_pos)")
    try:
        conn.execute(
            query,
            kwargs,
        )
        conn.commit()
    except IntegrityError:
        conn.rollback()


def insert_exon_query(**kwargs):
    conn = get_connection()
    query = text("INSERT INTO exons (entrez_id, exon_number, chromosome, product, sense, start_pos, end_pos) VALUES (:entrez_id, :exon_number, :chromosome, :product, :sense, :start_pos, :end_pos)")
    try:
        conn.execute(
            query,
            kwargs,
        )
        conn.commit()
    except IntegrityError:
        conn.rollback()


def create_region_query(organism, region):
    conn = get_connection()
    try:
        int(region)
    except ValueError:
        is_entrez_id = False
    else:
        is_entrez_id = True

    query = (
        "SELECT genes.entrez_id, genes.gene_symbol AS region_name, genes.start_pos AS start_pos, genes.end_pos AS end_pos, "
        "genes.sense, 'chr' || chromosomes.name AS chromosome_name, chromosomes.accession AS chromosome_accession FROM genes, chromosomes "
        "WHERE genes.chromosome=chromosomes.accession AND chromosomes.organism = :organism"
    )

    if is_entrez_id:
        query += " AND genes.entrez_id=:entrez_id"
    else:
        query += " AND genes.gene_symbol=:entrez_id"

    query = text(query)
    results = conn.execute(query, {'organism': organism, 'entrez_id': region})
    for row in results.mappings():
        return dict(row)


def get_chromosome_names(organism):
    conn = get_connection()
    query = text(
        "SELECT accession, CONCAT('chr', name) FROM chromosomes WHERE organism = :organism"
    )
    results = conn.execute(query, {'organism': organism})
    return dict([row for row in results]) or None


def get_library_info_by_gene(organism, genes, n_guides=6):
    conn = get_connection()
    # TODO: Do we need an ORDER BY here?
    #   See https://github.com/pritykinlab/guidescan-web/blob/master/src/guidescan_web/query/library_design.clj#L150
    query = text(
        "SELECT * FROM libraries WHERE organism = :organism AND gene_symbol IN (SELECT gene_symbol FROM genes WHERE entrez_id IN (SELECT entrez_id FROM genes WHERE gene_symbol = :gene)) LIMIT :n_guides"
    )

    return_value = {}
    for gene in genes:
        return_value[gene] = []
        results = conn.execute(query, {'organism': organism, 'gene': gene, 'n_guides': n_guides})
        for row in results.mappings():
            return_value[gene].append(dict(row))

    return return_value


def get_essential_genes(organism, n=1):
    conn = get_connection()
    query = text(
        "SELECT gene_symbol FROM essential_genes WHERE organism = :organism LIMIT :n"
    )
    results = conn.execute(query, {'organism': organism, 'n': n})
    return [r[0] for r in results]  # TODO: Ugly!


def get_control_guides(organism, n=1):
    conn = get_connection()
    # TODO: Order by?
    query = text(
        "SELECT * FROM libraries WHERE organism = :organism AND (grna_type='safe_targeting_control' OR grna_type='non_targeting_control') LIMIT :n"
    )
    results = conn.execute(query, {'organism': organism, 'n': n})
    return [dict(row) for row in results.mappings()]


@cache
def get_chromosome_interval_trees():
    conn = get_connection()
    query = text(
        "SELECT chromosome, start_pos, end_pos, exon_number, product FROM exons"
    )
    if conn is None:
        return {}
    results = conn.execute(query)

    chromosomes = {}
    for chr, start, end, exon_number, product in results:
        if chr not in chromosomes:
            chromosomes[chr] = IntervalTree()
        # Convert 1-indexed [start, end] to 0-indexed [start, end)
        chromosomes[chr][start - 1 : end] = exon_number, product

    return chromosomes
