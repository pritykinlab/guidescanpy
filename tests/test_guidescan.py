from guidescanpy.core.guidescan import cmd_enumerate


def test_enumerate_cas9_exact(index_prefix):
    kmers = ["AGAATATTTCGTACTTACAC", "ATGTGACACTACTCATACGA"]
    results = cmd_enumerate(
        kmers=kmers, pam="NGG", index_filepath_prefix=index_prefix, mismatches=0
    )
    results = results.to_dict(orient="records")
    assert results == [
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
    ]


def test_enumerate_cpf1_exact(index_prefix):
    kmers = ["GCATATAATATCAATTAATT", "ATTTATGCCGTCTGGGATTG"]
    results = cmd_enumerate(
        kmers=kmers,
        pam="TTTN",
        index_filepath_prefix=index_prefix,
        start=True,
        mismatches=0,
    )
    results = results.to_dict(orient="records")
    assert results == [
        {
            "id": "id_00000000",
            "sequence": "TTTNGCATATAATATCAATTAATT",
            "match_chrm": "NC_001224.1",
            "match_position": 12184,
            "match_strand": "-",
            "match_distance": 0,
            "match_sequence": "AATTAATTGATATTATATGCCAAA",
            "rna_bulges": 0,
            "dna_bulges": 0,
            "specificity": 1.0,
        },
        {
            "id": "id_00000001",
            "sequence": "TTTNATTTATGCCGTCTGGGATTG",
            "match_chrm": "NC_001146.8",
            "match_position": 72199,
            "match_strand": "+",
            "match_distance": 0,
            "match_sequence": "CAATCCCAGACGGCATAAATGAAA",
            "rna_bulges": 0,
            "dna_bulges": 0,
            "specificity": 1.0,
        },
    ]


def test_enumerate_arbitrary(index_prefix):
    # Sequences can be arbitrary in length and don't have to include PAMs at all
    kmers = ["AGAATATTTCGTA", "ATGTGACCTCATACGA"]
    results = cmd_enumerate(
        kmers=kmers,
        pam="",
        index_filepath_prefix=index_prefix,
        mismatches=1,
        alt_pam=None,
    )

    kmer0_exact_matches = results[
        (results.sequence == kmers[0])
        & (~results.match_position.isna())
        & (results.match_distance == 0)
    ]
    assert len(kmer0_exact_matches) == 10

    kmer0_distance1_matches = results[
        (results.sequence == kmers[0])
        & (~results.match_position.isna())
        & (results.match_distance == 1)
    ]
    assert len(kmer0_distance1_matches) == 53

    kmer1_exact_matches = results[
        (results.sequence == kmers[1])
        & (~results.match_position.isna())
        & (results.match_distance == 0)
    ]
    assert len(kmer1_exact_matches) == 0
