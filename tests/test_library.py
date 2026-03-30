from unittest.mock import patch
from guidescanpy.flask.blueprints.library import (
    library,
    OLIGO_OVERHANGS,
    ADAPTERS,
    BARCODES,
)

MOCK_GRNA = "ACGTACGTACGTACGTACGT"


def mock_library_side_effect(_organism, genes, _n_guides):
    # Helper mock to simulate returning one gRNA per gene
    return {gene: [{"grna": MOCK_GRNA}] for gene in genes}


@patch("guidescanpy.flask.blueprints.library.get_control_guides")
@patch("guidescanpy.flask.blueprints.library.get_essential_genes")
@patch("guidescanpy.flask.blueprints.library.get_library_info_by_gene")
def test_library_oligo_construction(mock_library_info, mock_essential, mock_controls):
    mock_library_info.side_effect = mock_library_side_effect
    mock_essential.return_value = []
    mock_controls.return_value = []

    result = library(
        organism="sacCer3",
        genes="CNE1",
        n_pools=1,
        n_guides=6,
    )

    grna = result["results"][0]["library"][0][0]

    # Verify forward oligo = 5' overhang + gRNA sequence
    assert grna["forward_oligo"] == OLIGO_OVERHANGS["5_prime"] + MOCK_GRNA

    # Verify reverse oligo = gRNA sequence + 3' overhang
    assert grna["reverse_oligo"] == MOCK_GRNA + OLIGO_OVERHANGS["3_prime"]

    # Verify full library oligo = F1 barcode + 5' adapter + gRNA + 3' adapter + R1 barcode
    assert (
        grna["library_oligo"]
        == BARCODES["5_prime"]["F1"]
        + ADAPTERS["5_prime"]
        + MOCK_GRNA
        + ADAPTERS["3_prime"]
        + BARCODES["3_prime"]["R1"]
    )


@patch("guidescanpy.flask.blueprints.library.get_control_guides")
@patch("guidescanpy.flask.blueprints.library.get_essential_genes")
@patch("guidescanpy.flask.blueprints.library.get_library_info_by_gene")
def test_library_single_pool_structure(
    mock_library_info, mock_essential, mock_controls
):
    mock_library_info.side_effect = mock_library_side_effect
    mock_essential.return_value = []
    mock_controls.return_value = []

    result = library(
        organism="sacCer3",
        genes="CNE1",
        n_pools=1,
        n_guides=6,
    )

    assert result["organism"] == "sacCer3"
    assert len(result["results"]) == 1
    assert result["results"][0]["pool_number"] == 0
    assert result["results"][0]["controls"] == []
    assert result["results"][0]["essential_genes"] == {}
