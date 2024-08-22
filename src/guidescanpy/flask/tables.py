from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Libraries(Base):
    __tablename__ = "libraries"

    grna = Column(String(1023), nullable=False, primary_key=True)
    organism = Column(String(1023), nullable=False)
    source = Column(String(1023), nullable=False)
    gene_symbol = Column(String(1023))
    grna_type = Column(String(1023), nullable=False, primary_key=True)
    chromosome = Column(String(1023))
    identifier = Column(String(1023))
    region_id = Column(String(1023))
    strand = Column(String(1023))
    position = Column(Integer)
    offtarget0 = Column(Integer, nullable=False)
    offtarget1 = Column(Integer, nullable=False)
    offtarget2 = Column(Integer, nullable=False)
    offtarget3 = Column(Integer, nullable=False)
    specificity = Column(Float)
    specificity_5pg = Column(Float)
    cutting_efficiency = Column(Float)


class Chromosomes(Base):
    __tablename__ = "chromosomes"

    accession = Column(String(1023), nullable=False, primary_key=True)
    name = Column(String(1023), nullable=False, primary_key=True)
    organism = Column(String(1023), nullable=False, primary_key=True)


class Genes(Base):
    __tablename__ = "genes"

    entrez_id = Column(Integer, nullable=False, primary_key=True)
    gene_symbol = Column(String(1023), nullable=False, primary_key=True)
    chromosome = Column(String(1023), nullable=False, primary_key=True)
    sense = Column(Boolean, nullable=False)
    start_pos = Column(Integer, nullable=False)
    end_pos = Column(Integer, nullable=False)


class Exons(Base):
    __tablename__ = "exons"

    entrez_id = Column(Integer, nullable=False, primary_key=True)
    exon_number = Column(Integer, nullable=False, primary_key=True)
    chromosome = Column(String(1023), nullable=False, primary_key=True)
    product = Column(String(1023))
    sense = Column(Boolean, nullable=False)
    start_pos = Column(Integer, nullable=False)
    end_pos = Column(Integer, nullable=False)


class EssentialGenes(Base):
    __tablename__ = "essential_genes"

    gene_symbol = Column(String(1023), nullable=False, primary_key=True)
    organism = Column(String(1023), nullable=False, primary_key=True)
