FROM docker.io/library/python:3.12

# git: pip install from GitHub; libcurl4: runtime dependency of the guidescan binary;
# wget: used by snakemake download rules
# RUN apt-get update && apt-get install -y --no-install-recommends git libcurl4 wget ca-certificates \
#     && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.9.28 /uv /usr/local/bin/uv

ENV \
    # show stdout/stderr eagerly
    PYTHONUNBUFFERED=1 \
    # to allow --mount=type=cache to work without copy warning from uv
    UV_LINK_MODE=copy \
    # stick to the python version explicitly defined in FROM
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Prebuilt guidescan binary from the guidescan-cli GitHub releases
ARG GUIDESCAN_VERSION=v2.2.1
RUN wget -qO- https://github.com/pritykinlab/guidescan-cli/releases/download/${GUIDESCAN_VERSION}/guidescan-${GUIDESCAN_VERSION}-Linux.tar.gz \
    | tar xz -C /usr/local bin/guidescan \
    && guidescan --version


# Note: there is no conda in this image, so `snakemake --use-conda` (needed only for
# the RS2 cutting-efficiency rule, rs2/env.yaml) will not work here.
# The build context is the repository root (see docker-compose.yml).

# Minimal COPYs to install the locked dependencies first, for speedy builds
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-install-project

# .git is not copied into the image, so the version comes in as a build arg (e.g. from `uvx setuptools-scm`)
ARG VERSION=0.0.0
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_GUIDESCANPY=${VERSION}

# Minimal COPYs to allow editable package install
COPY README.md ./
COPY src ./src
# --no-cache, since uv's cached build of the project wouldn't pick up a new VERSION
RUN uv sync --locked --no-cache

RUN mkdir /snakemake
COPY docker/snakemake /snakemake
WORKDIR /snakemake
