FROM continuumio/miniconda3

EXPOSE 5000

RUN mkdir /app/ && mkdir /app/src

COPY pyproject.toml /app
COPY src /app/src/

WORKDIR /app

RUN conda install -c conda-forge -c bioconda guidescan
RUN --mount=source=.git,target=.git,type=bind pip install --no-cache-dir -e .[web]