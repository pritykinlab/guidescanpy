create table if not exists libraries
(
    grna               varchar(1023) not null,
    organism           varchar(1023) not null,
    source             varchar(1023) not null,
    gene_symbol        varchar(1023),
    grna_type          varchar(1023) not null,
    chromosome         varchar(1023),
    identifier         varchar(1023),
    region_id          varchar(1023),
    strand             varchar(1023),
    position           integer,
    offtarget0         integer       not null,
    offtarget1         integer       not null,
    offtarget2         integer       not null,
    offtarget3         integer       not null,
    specificity        real,
    specificity_5pg    real,
    cutting_efficiency real,
    primary key (grna, grna_type)
);


create table if not exists chromosomes
(
    accession varchar(1023) not null
        primary key,
    name      varchar(1023) not null,
    organism  varchar(1023) not null
);


create table if not exists genes
(
    entrez_id   integer       not null,
    gene_symbol varchar(1023) not null,
    chromosome  varchar(1023) not null,
    sense       boolean       not null,
    start_pos   integer       not null,
    end_pos     integer       not null,
    primary key (entrez_id, gene_symbol, chromosome)
);


create table if not exists exons
(
    entrez_id   integer       not null,
    exon_number integer       not null,
    chromosome  varchar(1023) not null,
    product     varchar(1023),
    sense       boolean       not null,
    start_pos   integer       not null,
    end_pos     integer       not null,
    primary key (entrez_id, exon_number, chromosome)
);


create table if not exists essential_genes
(
    gene_symbol varchar(1023) not null,
    organism    varchar(1023) not null,
    primary key (gene_symbol, organism)
);
