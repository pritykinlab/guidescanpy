import pytest
import os.path
from guidescanpy.flask.core.parser import region_parser


def test_parse_txt():
    file = "RAD51\nZWF1\nchrII:5000-8000"
    parser = region_parser(file, organism="sacCer3")
    regions = list(region for region in parser)
    assert regions == [
        ("RAD51", "chrV", 349980, 351182),
        ("ZWF1", "chrXIV", 196426, 197943),
        ("chrII:5000-8000", "chrII", 5000, 8000),
    ]


def test_parse_txt_file(data_folder):
    file = os.path.join(data_folder, "sacCer3_regions.txt")
    parser = region_parser(file, organism="sacCer3")
    regions = list(region for region in parser)
    assert regions == [
        ("RAD51", "chrV", 349980, 351182),
        ("ZWF1", "chrXIV", 196426, 197943),
        ("chrII:5000-8000", "chrII", 5000, 8000),
    ]


def test_parse_bed(data_folder):
    file = os.path.join(data_folder, "sacCer3_regions.bed")
    parser = region_parser(file, organism="sacCer3")
    regions = list(region for region in parser)
    assert regions == [
        ("chrII:5866-5888", "chrII", 5866, 5888),
        ("chrII:5867-5889", "chrII", 5867, 5889),
        ("chrII:5871-5893", "chrII", 5871, 5893),
        ("chrII:5872-5894", "chrII", 5872, 5894),
        ("chrII:5860-5882", "chrII", 5860, 5882),
        ("chrII:5861-5883", "chrII", 5861, 5883),
        ("chrII:5891-5913", "chrII", 5891, 5913),
        ("chrII:5923-5945", "chrII", 5923, 5945),
    ]


def test_parse_gff(data_folder):
    file = os.path.join(data_folder, "sacCer3_regions.gff")
    parser = region_parser(file, organism="sacCer3")
    regions = list(region for region in parser)
    assert regions == [
        ("chrII:5000-6000", "chrII", 5000, 6000),
        ("chrII:5866-5888", "chrII", 5866, 5888),
    ]


def test_parse_gtf(data_folder):
    file = os.path.join(data_folder, "sacCer3_regions.gtf")
    parser = region_parser(file, organism="sacCer3")
    regions = list(region for region in parser)
    assert regions == [
        ("chrII:5000-6000", "chrII", 5000, 6000),
        ("chrII:5866-5888", "chrII", 5866, 5888),
    ]


def test_parse_unrecognized_extension(tmp_path):
    file_path = tmp_path / "sacCer3_regions.csv"
    file_path.write_text("")

    with pytest.raises(TypeError):
        region_parser(file_path, organism="sacCer3")


def test_parse_txt_empty_input():
    parser = region_parser("", organism="sacCer3")
    regions = list(region for region in parser)
    assert regions == []


def test_parse_unknown_gene_only():
    parser = region_parser("UNKNOWNGENE", organism="sacCer3")
    regions = list(region for region in parser)
    assert regions == []


def test_parse_unknown_and_real_genes():
    parser = region_parser("RAD51\nUNKNOWNGENE\nchrII:5000-8000", organism="sacCer3")
    regions = list(region for region in parser)
    assert regions == [
        ("RAD51", "chrV", 349980, 351182),
        ("chrII:5000-8000", "chrII", 5000, 8000),
    ]
