from guidescanpy.core.guidescan import cmd_enumerate


def test_enumerate(index_prefix):
    kmers = ["AGAATATTTCGTACTTACACNGG", "ATGTGACACTACTCATACGANGG"]
    results = cmd_enumerate(kmers_with_pam=kmers, index_filepath_prefix=index_prefix)
    assert isinstance(results, list)
    assert results == [
        {
            "id": "id_00000001",
            "sequence": "ATGTGACACTACTCATACGANGG",
            "match_chrm": "NC_001133.9",
            "match_position": 1079,
            "match_strand": "+",
            "match_distance": 0,
            "match_sequence": "ATGTGACACTACTCATACGAAGG",
            "rna_bulges": 0,
            "dna_bulges": 0,
            "specificity": 1.0,
        },
        {
            "id": "id_00000000",
            "sequence": "AGAATATTTCGTACTTACACNGG",
            "match_chrm": "NC_001133.9",
            "match_position": 882,
            "match_strand": "+",
            "match_distance": 0,
            "match_sequence": "AGAATATTTCGTACTTACACAGG",
            "rna_bulges": 0,
            "dna_bulges": 0,
            "specificity": 1.0,
        },
    ]
