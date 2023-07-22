FROM continuumio/miniconda3

RUN apt-get update && apt-get install -y build-essential
# Install and use mamba (faster) instead of conda
RUN conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*'
RUN pip install snakemake

RUN mkdir /snakemake
COPY snakemake /snakemake
WORKDIR /snakemake

RUN conda env update --name base --file env.yaml
