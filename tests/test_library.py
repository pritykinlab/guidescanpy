import pytest
from unittest.mock import patch
from guidescanpy.flask.blueprints.library import library


def mock_library_side_effect(_organism, genes, _n_guides):
    # Helper mock to simulate returning one gRNA per gene
    return {gene: [{"grna": "ACGTACGTACGTACGTACGT"}] for gene in genes}


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
    assert grna["forward_oligo"] == "CACCACGTACGTACGTACGTACGT"

    # Verify reverse oligo = gRNA sequence + 3' overhang
    assert grna["reverse_oligo"] == "ACGTACGTACGTACGTACGTCAAA"

    # Verify full library oligo = F1 barcode + 5' adapter + gRNA + 3' adapter + R1 barcode
    assert (
        grna["library_oligo"]
        == "AGGCACTTGCTCGTACGACGCGTCTCACACCACGTACGTACGTACGTACGTGTTTCGAGACGTTAAGGTGCCGGGCCCACAT"
    )


@patch("guidescanpy.flask.blueprints.library.get_control_guides")
@patch("guidescanpy.flask.blueprints.library.get_essential_genes")
@patch("guidescanpy.flask.blueprints.library.get_library_info_by_gene")
def test_library_basic_structure(mock_library_info, mock_essential, mock_controls):
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


@patch("guidescanpy.flask.blueprints.library.get_control_guides")
@patch("guidescanpy.flask.blueprints.library.get_essential_genes")
@patch("guidescanpy.flask.blueprints.library.get_library_info_by_gene")
def test_library_two_pools(mock_library_info, mock_essential, mock_controls):

    mock_library_info.side_effect = mock_library_side_effect
    mock_essential.return_value = []
    mock_controls.return_value = []

    # Use '\r\n' line splitting to account for original code
    result = library(
        organism="sacCer3",
        genes="CNE1\r\nRAD51",
        n_pools=2,
        n_guides=6,
    )

    # Expect one pool per gene when n_pools=2
    assert len(result["results"]) == 2
    assert result["results"][0]["pool_number"] == 0
    assert result["results"][1]["pool_number"] == 1
    assert len(result["results"][0]["library"]) == 1
    assert len(result["results"][1]["library"]) == 1


@pytest.mark.xfail(
    reason="known bug: split('\\r\\n') doesn't handle Unix line endings, fixed in fix-library-todos branch"
)
@patch("guidescanpy.flask.blueprints.library.get_control_guides")
@patch("guidescanpy.flask.blueprints.library.get_essential_genes")
@patch("guidescanpy.flask.blueprints.library.get_library_info_by_gene")
def test_library_unix_line_endings(mock_library_info, mock_essential, mock_controls):

    # Genes separated by \n should work the same as \r\n
    mock_library_info.side_effect = mock_library_side_effect
    mock_essential.return_value = []
    mock_controls.return_value = []

    result = library(
        organism="sacCer3",
        genes="CNE1\nRAD51",
        n_pools=1,
        n_guides=6,
    )

    assert len(result["results"][0]["library"]) == 2
