from guidescanpy.flask.blueprints.sequence import sequence


def test_sequence_sacCer3():
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
        "id_00000000": {
            "coordinate": "chrV:350994-351016:+",
            "specificity": 0.662504,
            "num-off-targets": 5,
            "off-target-summary": "0:0|1:0|2:0|3:1|4:4",
            "off-targets": {
                0: [],
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
            "num-off-targets": 1,
            "off-target-summary": "0:0|1:0|2:0|3:1|4:0",
            "off-targets": {
                0: [],
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
    }
