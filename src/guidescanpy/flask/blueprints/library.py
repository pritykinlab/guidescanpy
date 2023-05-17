import numpy as np
from flask import Blueprint, redirect, url_for, request
from guidescanpy.flask.db import (
    get_library_info_by_gene,
    get_essential_genes,
    get_control_guides,
)
from guidescanpy import config

bp = Blueprint("library", __name__)


ADAPTERS = {"5_prime": "CGTCTCACACC", "3_prime": "GTTTCGAGACG"}

BARCODES = {
    "5_prime": {
        "F1": "AGGCACTTGCTCGTACGACG",
        "F2": "GTGTAACCCGTAGGGCACCT",
        "F3": "CAGCGCCAATGGGCTTTCGA",
        "F4": "CAGCGCCAATGGGCTTTCGA",
        "F5": "CATGTTGCCCTGAGGCACAG",
        "F6": "GGTCGTCGCATCACAATGCG",
    },
    "3_prime": {
        "R1": "TTAAGGTGCCGGGCCCACAT",
        "R2": "GTCGAAGGACTGCTCTCGAC",
        "R3": "CGACAGGCTCTTAAGCGGCT",
        "R4": "CGGATCGTCACGCTAGGTAC",
        "R5": "CGGATCGTCACGCTAGGTAC",
        "R6": "CGTCACATTGGCGCTCGAGA",
    },
}

OLIGO_OVERHANGS = {"5_prime": "CACC", "3_prime": "CAAA"}


@bp.route("", methods=["GET"])
def library_endpoint(args={}):
    args = args or request.args
    if config.celery.eager:
        return library(**args)
    else:
        from guidescanpy.tasks import library as f

        result = f.delay(**args)
        return redirect(url_for("job_library.job", job_id=result.task_id))


def library(
    organism: str,
    genes: str,
    n_pools: int = 1,
    n_guides: int = 6,
    frac_essential: float = 0.0,
    frac_control: float = 0.0,
    append5: bool = False,
):
    # TODO: Why is this \r\n and not just \n?
    genes = genes.split("\r\n")

    library_info = get_library_info_by_gene(organism, genes, n_guides)

    genes_by_pool_index = np.array_split(np.array(genes), n_pools)
    results = []
    for i, genes in enumerate(genes_by_pool_index):

        n_essential_genes = round(frac_essential * len(genes))
        # TODO: randomize
        essential_genes = get_essential_genes(organism, n_essential_genes)
        essential_genes_library_info = get_library_info_by_gene(
            organism, essential_genes, n_guides
        )

        n_control_guides = round(
            frac_control * len(genes)
        )  # TODO: Clojure code does this, but it doesn't seem correct
        # TODO: randomize
        control_guides = get_control_guides(organism, n_control_guides)

        for gene in genes:
            this_library_info = library_info[gene]
            for grna in this_library_info:
                grna_seq = grna["grna"]
                grna["forward_oligo"] = OLIGO_OVERHANGS["5_prime"] + grna_seq
                grna["reverse_oligo"] = grna_seq + OLIGO_OVERHANGS["3_prime"]

                barcode_name_left = f"F{i+1}"
                barcode_name_right = f"R{i+1}"

                grna["adapter_name"] = f"{barcode_name_left}-{barcode_name_right}"
                adapter_seq = "G" + grna_seq[1:] if append5 else grna_seq
                grna["library_oligo"] = (
                    BARCODES["5_prime"][barcode_name_left]
                    + ADAPTERS["5_prime"]
                    + adapter_seq
                    + ADAPTERS["3_prime"]
                    + BARCODES["3_prime"][barcode_name_right]
                )

        result = {
            "pool_number": i,
            "library": [library_info[k] for k in genes],
            "essential_genes": essential_genes_library_info,
            "controls": control_guides,
        }
        results.append(result)

    return {"organism": organism, "results": results}
