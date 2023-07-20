## Running guidescan in docker

### Preparation

The .env file in this folder contains variables that are substituted in docker-compose.yml and made available to
the running container. At a minimum, the following POSTGRES variables are needed to make things work.

```
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
```

The following Docker volumes need to be created/made available to the `docker` process. If not present, these are created
automatically.

#### guidescan_data

This is the volume where the data files for `guidescan` live. The typical folder structure in this volume (once the
`guidescan_snakemake` service is run, see `Generating guidescan data` for details), looks as follows:

```
├── databases
│   ├── cas9
│   │   ├── sacCer3.bam
│   │   ├── sacCer3.bam.sorted
│   │   ├── sacCer3.bam.sorted.bai
│   │   └── sacCer3.sam
│   └── cpf1
│       ├── sacCer3.bam
│       ├── sacCer3.bam.sorted
│       ├── sacCer3.bam.sorted.bai
│       └── sacCer3.sam
├── indices
│   ├── sacCer3.index.forward
│   ├── sacCer3.index.gs
│   └── sacCer3.index.reverse
├── job_status
│   ├── add_sacCer3.txt
│   └── init_db.txt
├── kmers
│   ├── cas9
│   │   └── sacCer3.csv
│   └── cpf1
│       └── sacCer3.csv
└── raw
    ├── sacCer3_chr2acc
    ├── sacCer3.fna
    ├── sacCer3.fna.forward.dna
    ├── sacCer3.fna.gz
    ├── sacCer3.fna.reverse.dna
    └── sacCer3.gtf.gz
```

#### guidescan_postgres_data

This is the volume where the contents of the relational Postgres database for `guidescan` live.

### Generating guidescan data

Run `docker-compose up --build --abort-on-container-exit guidescan_snakemake`.

### Running Guidescan

Run `docker-compose up --build guidescan_app`.
