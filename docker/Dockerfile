FROM anaconda/miniconda 

RUN apt-get update && apt-get install -y build-essential
RUN apt-get install -y git zlib1g-dev libbz2-dev liblzma-dev

ENV CONDA_PLUGINS_AUTO_ACCEPT_TOS=true
# GCC 14 turns implicit declarations etc. into errors, breaking source builds of
# old pip packages in rs2/env.yaml (scikit-learn 0.16.1). -fPIC is needed because
# setting CFLAGS overrides pysam's bundled htslib defaults.
ENV CFLAGS="-fPIC -fpermissive"

# Install and use mamba (faster) instead of conda
# RUN conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*'
RUN conda install python=3.10 pip --yes
RUN conda install -c conda-forge -c bioconda guidescan --yes
RUN pip install "guidescanpy[dev] @ git+https://github.com/pritykinlab/guidescanpy.git"

RUN mkdir /snakemake
COPY snakemake /snakemake
WORKDIR /snakemake
