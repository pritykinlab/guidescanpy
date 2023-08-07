
[![CI](https://github.com/pritykinlab/guidescan/actions/workflows/main.yml/badge.svg)](https://github.com/pritykinlab/guidescan/actions/workflows/main.yml)

# Guidescan
Guidescan is a Python-based web application and command-line tool used in genomic editing. It aids researchers in analyzing CRISPR guide RNAs for targeted gene editing. Guidescan assesses factors like on-target activity, off-target effects, and other attributes, assisting in the design of effective genome-editing experiments.


## Documentation
See the [Wiki](https://github.com/pritykinlab/guidescanpy/wiki) for full documentation, examples, operational details and other information.

### Table of Contents
- [Running Guidescan in Docker](https://github.com/pritykinlab/guidescanpy/wiki/01-Running-Guidescan-in-Docker)
  	- [Prerequisites](https://github.com/pritykinlab/guidescanpy/wiki/01-Running-Guidescan-in-Docker#prerequisites)
	- [Preparation](https://github.com/pritykinlab/guidescanpy/wiki/01-Running-Guidescan-in-Docker#preparation)
	- [Generating Guidescan Data](https://github.com/pritykinlab/guidescanpy/wiki/01-Running-Guidescan-in-Docker#generating-guidescan-data)
	- [Running Guidescan](https://github.com/pritykinlab/guidescanpy/wiki/01-Running-Guidescan-in-Docker#running-guidescan)
- [Generating Data](https://github.com/pritykinlab/guidescanpy/wiki/02-Generating-Data)
	- [Why You Need to Read this Tutorial](https://github.com/pritykinlab/guidescanpy/wiki/02-Generating-Data#why-you-need-to-read-this-tutorial)
	- [Setting Environment Variables](https://github.com/pritykinlab/guidescanpy/wiki/02-Generating-Data#setting-environment-variables)
	- [Run Snakemake Workflow](https://github.com/pritykinlab/guidescanpy/wiki/02-Generating-Data#run-snakemake-workflow)
	- [Data File Structure](https://github.com/pritykinlab/guidescanpy/wiki/02-Generating-Data#data-file-structure)
- [Developer Setup](https://github.com/pritykinlab/guidescanpy/wiki/03-Developer-Setup)
	- [Prerequisites](https://github.com/pritykinlab/guidescanpy/wiki/03-Developer-Setup#prerequisites)
	- [Setting up Guidescan Environment](https://github.com/pritykinlab/guidescanpy/wiki/03-Developer-Setup#setting-up-guidescan-environment)
	- [Installation](https://github.com/pritykinlab/guidescanpy/wiki/03-Developer-Setup#installation)
	- [Data Generation](https://github.com/pritykinlab/guidescanpy/wiki/03-Developer-Setup#data-generation)
	- [Configuration](https://github.com/pritykinlab/guidescanpy/wiki/03-Developer-Setup#configuration)
	- [Run Unit Tests](https://github.com/pritykinlab/guidescanpy/wiki/03-Developer-Setup#run-unit-tests)
	- [Run the Project](https://github.com/pritykinlab/guidescanpy/wiki/03-Developer-Setup#run-the-project)
	- [Installing `guidescan` (Optional)](https://github.com/pritykinlab/guidescanpy/wiki/03-Developer-Setup#installing-guidescan-optional)
	- [Contributing to `guidescanpy`](https://github.com/pritykinlab/guidescanpy/wiki/03-Developer-Setup#contributing-to-guidescanpy)
- [Project Structure](https://github.com/pritykinlab/guidescanpy/wiki/04-Project-Structure)
- [Command Line Interface](https://github.com/pritykinlab/guidescanpy/wiki/05-Command-Line-Interface)
	- [Web](https://github.com/pritykinlab/guidescanpy/wiki/05-Command-Line-Interface#web)
	- [Decode](https://github.com/pritykinlab/guidescanpy/wiki/05-Command-Line-Interface#decode)
	- [Generate Kmers](https://github.com/pritykinlab/guidescanpy/wiki/05-Command-Line-Interface#generate-kmers)
	- [Initialize Database](https://github.com/pritykinlab/guidescanpy/wiki/05-Command-Line-Interface#initialize-database)
	- [Add Organism](https://github.com/pritykinlab/guidescanpy/wiki/05-Command-Line-Interface#add-organism)
	- [Filter Tag](https://github.com/pritykinlab/guidescanpy/wiki/05-Command-Line-Interface#filter-tag)
	- [Add Tag](https://github.com/pritykinlab/guidescanpy/wiki/05-Command-Line-Interface#add-tag)
