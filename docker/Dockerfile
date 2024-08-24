FROM continuumio/miniconda3

RUN apt-get update && apt-get install -y build-essential
RUN apt-get install -y zlib1g-dev libbz2-dev liblzma-dev

# Install and use mamba (faster) instead of conda
# RUN conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*'
RUN conda install python=3.10 pip --yes
RUN conda install -c conda-forge -c bioconda guidescan --yes
RUN pip install "guidescanpy[dev] @ git+https://github.com/pritykinlab/guidescanpy.git"

RUN mkdir /snakemake
COPY snakemake /snakemake
WORKDIR /snakemake
