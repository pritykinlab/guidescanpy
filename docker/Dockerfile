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
RUN uv venv /app/.venv \
    && uv pip install --python /app/.venv "guidescanpy[dev] @ git+https://github.com/pritykinlab/guidescanpy.git"

RUN mkdir /snakemake
COPY snakemake /snakemake
WORKDIR /snakemake
