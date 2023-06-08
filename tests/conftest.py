import os.path
import pytest
from guidescanpy.flask import create_app
from guidescanpy import config


@pytest.fixture(scope="session")
def app():
    return create_app(debug=True)


@pytest.fixture(scope="session")
def bam_file():
    return os.path.join(os.path.dirname(__file__), "data", "sacCer3.bam.sorted")


@pytest.fixture(scope="session")
def sacCer3_chromosome_names():
    return {
        "NC_001133.9": "chrI",
        "NC_001134.8": "chrII",
        "NC_001135.5": "chrIII",
        "NC_001136.10": "chrIV",
        "NC_001137.3": "chrV",
        "NC_001138.5": "chrVI",
        "NC_001139.9": "chrVII",
        "NC_001140.6": "chrVIII",
        "NC_001141.2": "chrIX",
        "NC_001142.9": "chrX",
        "NC_001143.9": "chrXI",
        "NC_001144.5": "chrXII",
        "NC_001145.3": "chrXIII",
        "NC_001146.8": "chrXIV",
        "NC_001147.6": "chrXV",
        "NC_001148.4": "chrXVI",
    }


@pytest.fixture(scope="session")
def sacCer3_region_CNE1():
    return {
        "entrez_id": 851241,
        "region_name": "CNE1",
        "start_pos": 37464,
        "end_pos": 38972,
        "sense": True,
        "chromosome_name": "chrI",
        "chromosome_accession": "NC_001133.9",
    }


@pytest.fixture(scope="session")
def index_prefix():
    index_dir = config.guidescan.index_files_path_prefix
    index_prefix = config.guidescan.index_files_path_map.sacCer3
    index_prefix = os.path.join(index_dir, index_prefix)
    return index_prefix


@pytest.fixture(scope="session")
def data_folder():
    return os.path.join(os.path.dirname(__file__), "data")
