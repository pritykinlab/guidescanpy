FROM continuumio/miniconda3

EXPOSE 5001

#COPY pyproject.toml /app
#COPY src /app/src/

RUN apt-get update && apt-get install -y build-essential
RUN conda install -c conda-forge -c bioconda guidescan
#RUN --mount=source=../.git,target=.git,type=bind pip install --no-cache-dir -e .[web]

RUN pip install guidescanpy[web]@git+https://github.com/pritykinlab/guidescanpy.git

RUN mkdir -p /app/src && mkdir -p /app/data/raw
WORKDIR /app
