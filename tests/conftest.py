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
def index_prefix():
    index_dir = config.guidescan.index_files_path_prefix
    index_prefix = config.guidescan.index_files_path_map.sacCer3
    index_prefix = os.path.join(index_dir, index_prefix)
    return index_prefix


@pytest.fixture(scope="session")
def data_folder():
    return os.path.join(os.path.dirname(__file__), "data")
