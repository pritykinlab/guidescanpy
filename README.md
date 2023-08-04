
[![CI](https://github.com/pritykinlab/guidescan/actions/workflows/main.yml/badge.svg)](https://github.com/pritykinlab/guidescan/actions/workflows/main.yml)

# Guidescan
[Some Description]


## Table of Contents
- [Run Guidescan in Docker](#run-guidescan-in-docker)
- [Run Guidescan Locally](#run-guidescan-locally)
	- [Prerequisites](#prerequisites)
	- [Installation](#installation)
	- [Run Snakemake workflow](#run-snakemake-workflow)
	- [Data Files Structure](#data-files-structure)
	- [Configuration](#configuration)
	- [Run the Project](#running-the-project)
- [Project Structure](#project-structure)
- [Command Line Interface](#command-line-interface)
	- [Web](#web)
	- [Decode](#decode)
	- [Generate Kmers](#generate-kmers)
	- [Initialize Database](#initialize-database)
	- [Add Organism](#add-organism)
	- [Filter Tag](#filter-tag)
	- [Add Tag](#add-tag)

## Run Guidescan in Docker
For detailed instructions on running Guidescan in Docker, refer to this [page](https://github.com/pritykinlab/guidescanpy/tree/main/docker#running-guidescan-in-docker).
## Run Guidescan Locally
### Prerequisites
To run Guidescan locally, make sure you have the following prerequisites installed:

- [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) (miniconda or anaconda)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Redis](https://redis.io/docs/getting-started/installation/)
- [Snakemake](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html)  (version 3.9.0 or higher)

### Installation
Install the package and add optional dependencies from source
```
git+https://github.com/pritykinlab/guidescanpy.git#egg=guidescanpy[web,dev]
```

### Run Snakemake workflow
Snakemake workflow is used to initialize databases and generate required data for this project. Conda is used to automatically create software environments for rules.


Here is a DAG for the workflow:
![Snakemake DAG](https://github.com/pritykinlab/guidescanpy/blob/main/docker/snakemake/rulegraph.png)


1.  **Set environment variables**
	- `POSTGRES_DB`: The name of the postgres database. The default is `guidescan`.
	- `POSTGRES_HOST`: The database host. The default is `localhost`.
	- `POSTGRES_USER`:  The username for the database. The default is `scott`.
	- `POSTGRES_PASSWORD`: The password for the database user. The default is `tiger`.

2.  **Run Snakemake workflow**

	Navigate to the `docker/snakemake` folder.

	- To generate the full databases, use the following command:
		```
		snakemake --cores 1 --use-conda
		```
		Running this command will generate `bam` files for all available organisms and enzymes listed in [`config.json`](https://github.com/pritykinlab/guidescanpy/blob/main/docker/snakemake/config.json). Keep in mind that this process may be time and resource-intensive due to the large amount of data involved.

	- Alternatively, users can customize the databases using the `--config` flag. You can specify the desired `organisms`, `enzymes`, and `max_kmers` to generate partial databases:
		- `max_kmers (int)`: Defines the number of kmers to generate. The default is `inf`.
		- `organisms (list)`: Generates database(s) for the specified organism(s). The default is `["sacCer3", "hg38", 	"ce11", "dm6", "mm10", "mm39", "rn6", "t2t_chm13"]`.
		- `enzymes (list)`: Generates database(s) for the specified enzyme(s). The default is `["cas9", "cpf1"]`.

		 For example, if you want to generate the `sacCer3/cas9` databases with only the first 1000 `kmers`, use the following command:
		```
		snakemake --cores 1 --use-conda --config max_kmers=1000 organisms=[\"sacCer3\"] enzymes=[\"cas9\"]
		```
	**Note:** For development and testing purposes, we only require the `sacCer3/cas9` database to be generated.


### Data File Structure

After running the workflow with `--config organisms=[\"sacCer3\"]`, the output data folder should have the following structure:

	├── databases
	│   ├── cas9
	│   │   ├── sacCer3.bam
	│   │   ├── sacCer3.bam.sorted
	│   │   ├── sacCer3.bam.sorted.bai
	│   │   └── sacCer3.sam
	│   └── cpf1
	│       ├── sacCer3.bam
	│       ├── sacCer3.bam.sorted
	│       ├── sacCer3.bam.sorted.bai
	│       └── sacCer3.sam
	├── indices
	│   ├── sacCer3.index.forward
	│   ├── sacCer3.index.gs
	│   └── sacCer3.index.reverse
	├── job_status
	│   ├── add_sacCer3.txt
	│   └── init_db.txt
	├── kmers
	│   ├── cas9
	│   │   └── sacCer3.csv
	│   └── cpf1
	│       └── sacCer3.csv
	└── raw
	    ├── sacCer3_chr2acc
	    ├── sacCer3.fna
	    ├── sacCer3.fna.forward.dna
	    ├── sacCer3.fna.gz
	    ├── sacCer3.fna.reverse.dna
	    └── sacCer3.gtf.gz
The `.bam.sorted` files are the databases the backend is using.

### Configuration
1. **Environment Virables**
	Set the following environment variables:
	- `BAM_PATH`: Path to the bam files, commonly as  `path-to-guidescanpy/docker/snakemake/data/databases`
	- `INDEX_PATH`: Path to the indices file, commonly as `path-to--guidescanpy/docker/snakemake/data/indices`
	- `CELERY_BACKEND`: The backend used to store the of asynchronous tasks executed by Celery workers, commonly as `redis://localhost`
	- `CELERY_BROKER`: The broker in Celery, commonly as redis://localhost
	- `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PASSWORD`, `POSTGRES_USER`: Configure them according to the parameters listed in the [Run Snakemake Workflow](#run-snakemake-workflow) section 1.



### Run the Project
1. **Run Celery Worker**
	```
	celery -A guidescanpy.tasks.app worker -l INFO
	```
2. **Run Guidescan Web**
	```
	guidescanpy web
	```

## Project Structure
This project consists of several key directories and files, organized as follows:
1. **`docker/`**: Contains Docker-related files, including the Dockerfile, docker-compose.yml and snakemake related files.
	- **`snakemake/`**: Contains Snakefile, snakemake config file, and environment files for snakemake rules.
2. **`src/guidescanpy/`**: Contains the main source code for Guidescan.
	- **`commands/`**: Contains various command-line utilities for the project.
	- **`flask/`**: Contains the Flask application components.
		- **`core/`**: Class `GenomeStructure` is defined in `genome.py`, which contains the core code for the implementation of  the query functionality.
		- **`blueprints/`**: Contains the blueprints for the Flask app.
		- **`templates/`**: Contains HTML templates.
		- **`db.py`**: The functions related to database operations and querying.
	- **`tasks/`**: Contains Celery tasks definitions.
	- **`config.json`**: The main configuration file for the project.
3. **`tests/`**: Contains pytest unit test files and test data files. `@patch` decorators helps prevent actual database communication.
4. **`pyproject.toml`**: The TOML configuration file for project metadata and dependencies.

## Command Line Interface
Guidescanpy has a command line interface to perform certain functionalities, mostly for developers use. To use the CLI tool, run the command in the format:
```
guidescanpy command [options] [arguments]
```

### Web
```
guidescanpy web
```
This command will start the Guidescanpy web application on localhost. The default port is 5001, with debug mode on. Port number and debug mode can be changed in [`/src/guidescanpy/__main__.py`](https://github.com/pritykinlab/guidescanpy/blob/main/src/guidescanpy/__main__.py).

### Decode
```
guidescanpy decode [options] [arguments]
```
This command will decode the given bam file to a human-readable data file.

- **Positional arguments:**
	- `grna_database`:  SAM/BAM file containing Guidescan2 processed gRNAs. Commonly as `guidescanpy/docker/snakemake/data/databases/[enzyme]/[organism].bam.sorted`.
	- `fasta_file`  FASTA file for resolving off-target sequences. Commonly as `guidescanpy/docker/snakemake/data/raw/[organism].fna`.
	- `chr2acc_file`  chr2acc file for chromosome resolution. Commonly as `guidescanpy/docker/snakemake/data/raw/[organism]_chr2acc`.

- **Options and flags:**
	- `-h`, `--help`:  Show this help message and exit.
	- `--region REGION`: One or more region strings.
	- `--mode {succinct,complete}`: Succinct or complete off-target information.

- **Output**:
Print a CSV-formatted output with the following columns:
	- `id`: The identifier for each sequence.
	- `sequence`: The target DNA sequence.
	- `chromosome`: The chromosome where the target sequence is located.
	- `position`: The position of the target sequence on the chromosome.
	- `sense`: The direction of the sequence (`+` or `-`).
	- `distance_0_matches`: The number of perfect matches found.
	- `distance_1_matches`: The number of matches with 1 mismatch found.
	- `distance_2_matches`: The number of matches with 2 mismatches found.
	- `distance_3_matches`: The number of matches with 3 mismatches found.
	- `specificity`: The specificity of the sequence.
	- `cutting_efficiency`: The cutting efficiency of the sequence.

- **Example**
	```
	guidescanpy decode data/databases/cas9/sacCer3.bam.sorted data/raw/sacCer3.fna data/raw/sacCer3_chr2acc
	```
	The output is:
	```
	id,sequence,chromosome,position,sense,distance_0_matches,distance_1_matches,distance_2_matches,distance_3_matches,specificity,cutting_efficiency
	NC_001133.9:44:-,AGGATGTGTGTGTGTGGGTGNGG,NC_001133.9,44,-,0,0,4,20,0.10518199950456619,0.46371179819107056
	NC_001133.9:49:-,GTGTTAGGATGTGTGTGTGTNGG,NC_001133.9,49,-,0,0,2,2,0.54339200258255,0.4851852059364319
	NC_001133.9:50:-,AGTGTTAGGATGTGTGTGTGNGG,NC_001133.9,50,-,0,0,1,2,0.8631880283355713,0.5173904299736023
	NC_001133.9:64:-,GGCTGTGTTAGGGTAGTGTTNGG,NC_001133.9,64,-,0,0,3,5,0.39531800150871277,0.38337841629981995
	NC_001133.9:74:-,GTTAGATTAGGGCTGTGTTANGG,NC_001133.9,74,-,0,0,0,4,0.4179899990558624,0.5174511671066284
	......
	```
### Generate Kmers
```
guidescanpy generate-kmers [options] [arguments]
```
This command will generate kmers from the given FASTA file, based on the specified PAM sequence.
- **Positional arguments:**
	- `fasta`:  FASTA file to use as a reference for kmer generation. Commonly as `guidescanpy/docker/snakemake/data/raw/[organism].fna`.

- **Options and flags:**
	- `-h`, `--help`:  Show this help message and exit.
	- `--pam PAM` Protospacer adjacent motif to match. The default is `NGG`.
	- `--kmer-length KMER_LENGTH` Length of kmers to generate. The default is `20`.
	- `--min-chr-length MIN_CHR_LENGTH` Minimum chromosome length to consider for kmer generation. The default is `0`.
	- `--prefix PREFIX` Prefix to use for kmer identifiers. The default is no prefix.
	- `--start` Match PAM at start of kmer instead at end (default).
	- `--max-kmers` MAX_KMERS Maximum number of kmers to generate. The default is no limit.

- **Output**:
Print a CSV-formatted output with the following columns:
	- `id`: The identifier for each sequence.
	- `sequence`: The target DNA sequence.
	- `pam`: The PAM of the target.
	- `chromosome`: The chromosome where the target sequence is located.
	- `position`: The position of the target sequence on the chromosome.
	- `sense`: The direction of the sequence (`+` or `-`).

- **Example**
	```
	guidescanpy generate-kmers data/raw/sacCer3.fna --max-kmers 100
	```
	The output is:
	```
	id,sequence,pam,chromosome,position,sense
	NC_001133.9:882:+,AGAATATTTCGTACTTACAC,NGG,NC_001133.9,882,+
	NC_001133.9:1079:+,ATGTGACACTACTCATACGA,NGG,NC_001133.9,1079,+
	NC_001133.9:1112:+,AGTCAAGACGATACTGTGAT,NGG,NC_001133.9,1112,+
	NC_001133.9:1128:+,TGATAGGTACGTTATTTAAT,NGG,NC_001133.9,1128,+
	NC_001133.9:1340:+,ATTTTACGTGTCAAAAAATG,NGG,NC_001133.9,1340,+
	NC_001133.9:1488:+,CAGCGACTCATTTTTATTTA,NGG,NC_001133.9,1488,+
	...... (100 records in total)
	```

### Initialize Database
```
guidescanpy init-db
```
This command serves to initialize the PostgreSQL database by creating five tables: `libraries`, `chromosomes`, `genes`, `exons`, and `essential_genes`, if they do not already exist.

### Add Organism
```
guidescanpy add-organism [options] [arguments]
```
This command will add all data of the given organism to the PostgreSQL database.
- **Positional arguments:**
	- `organism`: Organism that needs to be added to the database.
	- `gtf_gz`: The gtf.gz file for the organism. Commonly as `guidescanpy/docker/snakemake/data/raw/[organism].gtf.gz`
	- `chr2acc`: The chr2acc file for the organism. Commonly as `guidescanpy/docker/snakemake/data/raw/[organism]_chr2acc`

- **Options and flags:**
	- `-h`, `--help`:  show this help message and exit

- **Example:**:
	```
	guidescanpy add-organism sacCer3 data/raw/sacCer3.gtf.gz data/raw/sacCer3_chr2acc
	```


### Filter Tag
```
guidescanpy filter-tag [options]
```
This command can filter a SAM/BAM file based on the number of offtargets at a given distance.

- **Options and flags**
		- `-h`, `--help`:  Show this help message and exit
		- `--input INPUT`, `-i INPUT` (Required): Path to the input sam/bam file.
		- `--output OUTPUT`, `-o OUTPUT` (Required): Path to the output sam/bam file.
		- `--k0 K0`: Max number of off-targets at distance 0. The default is `1`.
		- `--k1 K1`: Max number of off-targets at distance 1. The default is `0`.
		- `--k2 K2`: Max number of off-targets at distance 2. The default is `inf`.
		- `--k3 K3`: Max number of off-targets at distance 3. The default is `inf`.

- **Output**
A filtered SAM/BAM file.

- **Example**
	```
	guidescanpy filter-tag --input data/databases/cas9/sacCer3.sam --output data/databases/cas9/sacCer3.bam
	```




### Add Tag
```
guidescanpy add-tag [options] [arguments]
```
This **incomplete** command can add new tags to the SAM/BAM files. It was originally designed to add `ce` tag to the SAM files generated by `guidescan enumerate`, but due to model version incompatibility, this command wasn't put into use. It may have potential usage in the future.

- **Positional arguments:**
	- `tag`: List of tags to add.

- **Options and flags:**
	- `-h`, `--help`: Show this help message and exit
	- `--input INPUT` (Required), `-i INPUT`: Path to the input sam/bam file.
	- `--output OUTPUT` (Required), `-o OUTPUT`: Path to the output sam/bam file.

- **Output**
The SAM/BAM file with added tag(s).
