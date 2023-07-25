import os.path
from unittest.mock import patch
from guidescanpy.commands.add_organism import insert_chromosome


@patch("guidescanpy.commands.add_organism.insert_chromosome_query")
def test_insert_chromosome_chr2acc_format(_):
    file = os.path.join(os.path.dirname(__file__), "data", "sacCer3_chr2acc.txt")
    accessions = insert_chromosome("sacCer3", file)

    assert accessions == [
        "NC_001133.9",
        "NC_001134.8",
        "NC_001135.5",
        "NC_001136.10",
        "NC_001137.3",
        "NC_001138.5",
        "NC_001139.9",
        "NC_001140.6",
        "NC_001141.2",
        "NC_001142.9",
        "NC_001143.9",
        "NC_001144.5",
        "NC_001145.3",
        "NC_001146.8",
        "NC_001147.6",
        "NC_001148.4",
    ]


@patch("guidescanpy.commands.add_organism.insert_chromosome_query")
def test_insert_chromosome_chromAlias_format(_):
    file = os.path.join(os.path.dirname(__file__), "data", "hs1.chromAlias.txt")
    accessions = insert_chromosome("t2t_chm13", file)

    assert accessions == [
        "NC_060925.1",
        "NC_060934.1",
        "NC_060935.1",
        "NC_060936.1",
        "NC_060937.1",
        "NC_060938.1",
        "NC_060939.1",
        "NC_060940.1",
        "NC_060941.1",
        "NC_060942.1",
        "NC_060943.1",
        "NC_060926.1",
        "NC_060944.1",
        "NC_060945.1",
        "NC_060946.1",
        "NC_060927.1",
        "NC_060928.1",
        "NC_060929.1",
        "NC_060930.1",
        "NC_060931.1",
        "NC_060932.1",
        "NC_060933.1",
        "NC_060947.1",
        "NC_060948.1",
    ]
