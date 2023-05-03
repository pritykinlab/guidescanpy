import os.path
import pytest
from guidescanpy.flask import create_app
from guidescanpy import config


@pytest.fixture(scope="session")
def app():
    return create_app(debug=True)


@pytest.fixture(scope="session")
def bam_file():
    bam_dir = config.guidescan.grna_database_path_prefix
    bam_filename = config.guidescan.grna_database_path_map.sacCer3.cas9
    bam_file = os.path.join(bam_dir, bam_filename)
    return bam_file
