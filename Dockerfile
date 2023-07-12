FROM continuumio/miniconda3

EXPOSE 5001

RUN mkdir /app/ && mkdir /app/src

COPY pyproject.toml /app
COPY src /app/src/

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN conda install -c conda-forge -c bioconda guidescan
RUN --mount=source=../.git,target=.git,type=bind pip install --no-cache-dir -e .[web]

# pip install guidescanpy[web]@git+https://github.com/pritykinlab/guidescanpy.git
