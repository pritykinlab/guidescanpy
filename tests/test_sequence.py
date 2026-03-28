from guidescanpy.flask.blueprints.sequence import sequence
import pytest


def test_cas9_sequences_sacCer3():
    args = {
        "organism": "sacCer3",
        "enzyme": "cas9",
        "sequences": "CCAGATCCAAAGAAGCCTAT\r\nGCCATAATATTACCACCGAT",
        "mismatches": 4,
    }

    results = sequence(args)

    # Note: For these exact sequences,
    # The old webapp reported specificity values of 0.72 and 0.93 respectively.
    #     We report 0.66 and 0.93 here.
    #     This is because specificity calculation during legacy db generation considered max offtargets up to 3,
    #     while reporting off-targets up to distance 4.
    #
    #  We don't have these limitations since we do a real-time search here, so these values are deemed correct
    #  going forward.

    assert results == {
        "organism": "sacCer3",
        "matches": {
            "id_00000000": {
                "coordinate": "chrV:350994-351016:+",
                "specificity": 0.662504,
                "sequence": "CCAGATCCAAAGAAGCCTATNGG",
                "num-exact-matches": 1,
                "num-inexact-matches": 5,
                "num-off-targets": 6,
                "off-target-summary": "0:1 | 1:0 | 2:0 | 3:1 | 4:4",
                "off-targets": {
                    0: [
                        {
                            "position": 350994,
                            "direction": "+",
                            "distance": 0,
                            "accession": "NC_001137.3",
                            "coordinate": "chrV:350994-351016:+",
                        }
                    ],
                    1: [],
                    2: [],
                    3: [
                        {
                            "position": 225904,
                            "direction": "-",
                            "distance": 3,
                            "accession": "NC_001140.6",
                            "coordinate": "chrVIII:225904-225926:-",
                        }
                    ],
                    4: [
                        {
                            "position": 1221487,
                            "direction": "-",
                            "distance": 4,
                            "accession": "NC_001136.10",
                            "coordinate": "chrIV:1221487-1221509:-",
                        },
                        {
                            "position": 262636,
                            "direction": "+",
                            "distance": 4,
                            "accession": "NC_001144.5",
                            "coordinate": "chrXII:262636-262658:+",
                        },
                        {
                            "position": 418914,
                            "direction": "+",
                            "distance": 4,
                            "accession": "NC_001143.9",
                            "coordinate": "chrXI:418914-418936:+",
                        },
                        {
                            "position": 335750,
                            "direction": "+",
                            "distance": 4,
                            "accession": "NC_001139.9",
                            "coordinate": "chrVII:335750-335772:+",
                        },
                    ],
                },
            },
            "id_00000001": {
                "coordinate": "chrV:351009-351031:-",
                "specificity": 0.936281,
                "sequence": "GCCATAATATTACCACCGATNGG",
                "num-exact-matches": 1,
                "num-inexact-matches": 1,
                "num-off-targets": 2,
                "off-target-summary": "0:1 | 1:0 | 2:0 | 3:1 | 4:0",
                "off-targets": {
                    0: [
                        {
                            "position": 351009,
                            "direction": "-",
                            "distance": 0,
                            "accession": "NC_001137.3",
                            "coordinate": "chrV:351009-351031:-",
                        }
                    ],
                    1: [],
                    2: [],
                    3: [
                        {
                            "position": 30804,
                            "direction": "-",
                            "distance": 3,
                            "accession": "NC_001143.9",
                            "coordinate": "chrXI:30804-30826:-",
                        }
                    ],
                    4: [],
                },
            },
        },
    }


def test_arbitrary_sequences_sacCer3():
    args = {
        "organism": "sacCer3",
        "enzyme": None,  # This key indicates that we're searching for arbitrary sequences, with no PAM/alt-PAM
        "sequences": "AGAATATTTCGTA\r\nATGTGACCTCATACGA",
        "mismatches": 1,
    }

    results = sequence(args)
    assert results["matches"]["id_00000000"]["off-target-summary"] == "0:10 | 1:53"
    assert results["matches"]["id_00000001"]["off-target-summary"] == "0:0 | 1:0"
    print(results)


def test_too_many_mismatches():
    # Mismatches > 6 should raise RuntimeError
    args = {
        "organism": "sacCer3",
        "enzyme": "cas9",
        "sequences": "CCAGATCCAAAGAAGCCTAT",
        "mismatches": 7,
    }

    try:
        sequence(args)
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass


def test_sequence_invalid_enzyme():
    # Invalid enzyme should raise RuntimeError
    args = {
        "organism": "sacCer3",
        "enzyme": "incorrect_enzyme",
        "sequences": "CCAGATCCAAAGAAGCCTAT",
        "mismatches": 4,
    }

    try:
        sequence(args)
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass


def test_sequence_too_short():
    # Sequence shorter than min_sequence_length should raise GuidescanException
    args = {
        "organism": "sacCer3",
        "enzyme": "cas9",
        "sequences": "ACGT",
        "mismatches": 4,
    }

    try:
        sequence(args)
        assert False, "Expected GuidescanException"
    except Exception as e:
        assert "not between" in str(e)


def test_sequence_too_long():
    # Sequence longer than max_sequence_length should raise GuidescanException
    args = {
        "organism": "sacCer3",
        "enzyme": "cas9",
        "sequences": "ACGT" * 10,  # 40 nucleotides, max is 30
        "mismatches": 4,
    }

    try:
        sequence(args)
        assert False, "Expected GuidescanException"
    except Exception as e:
        assert "not between" in str(e)


def test_too_many_sequences():
    # More sequences than max_sequences should raise GuidescanException
    sequences = "\r\n".join(["CCAGATCCAAAGAAGCCTAT"] * 11)  # 11 sequences, max is 10
    args = {
        "organism": "sacCer3",
        "enzyme": "cas9",
        "sequences": sequences,
        "mismatches": 4,
    }

    try:
        sequence(args)
        assert False, "Expected GuidescanException"
    except Exception as e:
        assert "sequences allowed" in str(e)


@pytest.mark.xfail(
    reason="known bug: split('\\r\\n') doesn't handle Unix line endings, fixed in fix-seqence-todos branch"
)
def test_sequence_unix_line_endings():

    # Sequences separated by \n should work the same as \r\n
    args = {
        "organism": "sacCer3",
        "enzyme": None,
        "sequences": "AGAATATTTCGTA\nATGTGACCTCATACGA",
        "mismatches": 1,
    }

    results = sequence(args)
    assert results["matches"]["id_00000000"]["off-target-summary"] == "0:10 | 1:53"
    assert results["matches"]["id_00000001"]["off-target-summary"] == "0:0 | 1:0"
