
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
	- [Project Structure](#project-structure)
	- [Configuration](#configuration)
	- [Run the Project](#running-the-project)

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

### Project Structure
[explain main files]

### Configuration
1. **Environment Virables**
	Set the following environment variables:
	- `BAM_PATH`: Path to the bam files, commonly as  `path-to-guidescanpy/docker/snakemake/data/databases`
	- `INDEX_PATH`: Path to the indices file, commonly as `path-to--guidescanpy/docker/snakemake/data/indices`
	- `CELERY_BACKEND`: The backend used to store the of asynchronous tasks executed by Celery workers, commonly as `redis://localhost`
	- `CELERY_BROKER`: The broker in Celery, commonly as redis://localhost
	- `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PASSWORD`, `POSTGRES_USER`: Configure them according to the parameters listed in the [Run Snakemake Workflow](#run-snakemake-workflow) section 1.



### Run the Project
