import json
import numpy as np
import pandas as pd
import os.path
from unittest.mock import patch
import pickle
from guidescanpy.flask.core.genome import get_genome_structure


def assert_equal_offtargets(legacy, new):
    for x, y in zip(legacy["off-targets"], new["off-targets"]):
        for _x, _y in zip(x, y):
            assert _x["position"] == _y["position"]
            assert _x["chromosome"] == _y["chromosome"]
            assert (
                _x["direction"] == "positive" if _y["direction"] == "+" else "negative"
            )
            assert _x["distance"] == _y["distance"]
            assert _x["accession"] == _y["accession"]


def load_saved_data(data_path):
    with open(data_path) as file:
        data = json.load(file)
    return pd.DataFrame(data[0][1])


@patch("guidescanpy.flask.core.genome.get_chromosome_names")
def test_genome_structure(patched_fn, bam_file, sacCer3_chromosome_names):
    patched_fn.return_value = sacCer3_chromosome_names
    genome_structure = get_genome_structure(organism="sacCer3", bam_filepath=bam_file)

    genome = genome_structure.genome
    assert genome[0][0:3] == (230218, 813184, 316620)
    assert genome[1][0:3] == ("NC_001133.9", "NC_001134.8", "NC_001135.5")
    assert np.allclose(
        genome_structure.absolute_genome[0:4], [0, 230218, 1043402, 1360022]
    )
    assert genome_structure.off_target_delim == -12157106


@patch("guidescanpy.flask.core.parser.create_region_query")
@patch("guidescanpy.flask.core.genome.get_chromosome_names")
def test_genome_structure_parse_CNE1(
    patched_fn1, patched_fn2, bam_file, sacCer3_chromosome_names, sacCer3_region_CNE1
):
    patched_fn1.return_value = sacCer3_chromosome_names
    patched_fn2.return_value = sacCer3_region_CNE1
    genome_structure = get_genome_structure(organism="sacCer3", bam_filepath=bam_file)
    region = genome_structure.parse_regions("CNE1")[0]
    assert region["region-name"] == "CNE1"
    assert region["chromosome-name"] == "chrI"
    assert region["coords"] == ("chrI", 37464, 38972)


@patch("guidescanpy.flask.core.genome.get_chromosome_interval_trees")
@patch("guidescanpy.flask.core.genome.get_chromosome_names")
def test_genome_structure_query_manual(
    patched_fn1, patched_fn2, data_folder, bam_file, sacCer3_chromosome_names
):
    patched_fn1.return_value = sacCer3_chromosome_names
    patched_fn2.return_value = pickle.load(
        open(os.path.join(data_folder, "sacCer3_chrI_II_IX_itrees.pkl"), "rb")
    )
    genome_structure = get_genome_structure(organism="sacCer3", bam_filepath=bam_file)
    # manually selected region on chrI for CNE1 gene
    region = genome_structure.parse_regions("chrI:37464-38972")[0]
    results = genome_structure.query(region, enzyme="cas9", bam_filepath=bam_file)
    assert len(results) == 150


@patch("guidescanpy.flask.core.genome.get_chromosome_interval_trees")
@patch("guidescanpy.flask.core.parser.create_region_query")
@patch("guidescanpy.flask.core.genome.get_chromosome_names")
def test_genome_structure_query_CNE1(
    patched_fn1,
    patched_fn2,
    patched_fn3,
    data_folder,
    bam_file,
    sacCer3_chromosome_names,
    sacCer3_region_CNE1,
):
    patched_fn1.return_value = sacCer3_chromosome_names
    patched_fn2.return_value = sacCer3_region_CNE1
    patched_fn3.return_value = pickle.load(
        open(os.path.join(data_folder, "sacCer3_chrI_II_IX_itrees.pkl"), "rb")
    )
    genome_structure = get_genome_structure(organism="sacCer3", bam_filepath=bam_file)
    region = genome_structure.parse_regions("CNE1")[0]
    results = genome_structure.query(
        region,
        enzyme="cas9",
        as_dataframe=True,
        legacy_ordering=True,
        bam_filepath=bam_file,
    )

    old_results = load_saved_data(os.path.join(data_folder, "query_CNE1.json"))
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results["specificity"], results["specificity"]))
    assert np.all(
        np.isclose(old_results["cutting-efficiency"], results["cutting-efficiency"])
    )
    assert np.all(old_results["sequence"] == results["sequence"])
    assert np.all(old_results["start"] == results["start"])
    assert np.all(old_results["end"] == results["end"])

    assert_equal_offtargets(old_results, results)


@patch("guidescanpy.flask.core.genome.get_chromosome_interval_trees")
@patch("guidescanpy.flask.core.genome.get_chromosome_names")
def test_genome_structure_query_manual_filter_annotated(
    patched_fn1, patched_fn2, data_folder, bam_file, sacCer3_chromosome_names
):
    patched_fn1.return_value = sacCer3_chromosome_names
    patched_fn2.return_value = pickle.load(
        open(os.path.join(data_folder, "sacCer3_chrI_II_IX_itrees.pkl"), "rb")
    )
    genome_structure = get_genome_structure(organism="sacCer3", bam_filepath=bam_file)
    region = genome_structure.parse_regions("chrII:5000-10000")[0]
    results = genome_structure.query(
        region,
        enzyme="cas9",
        filter_annotated=True,
        as_dataframe=True,
        legacy_ordering=True,
        bam_filepath=bam_file,
    )
    old_results = load_saved_data(
        os.path.join(
            data_folder,
            "query_manual_filter_annotated.json",
        )
    )

    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results["specificity"], results["specificity"]))
    assert np.all(
        np.isclose(old_results["cutting-efficiency"], results["cutting-efficiency"])
    )
    assert np.all(old_results["sequence"] == results["sequence"])
    assert np.all(old_results["start"] == results["start"])
    assert np.all(old_results["end"] == results["end"])

    assert_equal_offtargets(old_results, results)


@patch("guidescanpy.flask.core.genome.get_chromosome_interval_trees")
@patch("guidescanpy.flask.core.parser.create_region_query")
@patch("guidescanpy.flask.core.genome.get_chromosome_names")
def test_genome_structure_query_CNE1_min_specificity(
    patched_fn1,
    patched_fn2,
    patched_fn3,
    data_folder,
    bam_file,
    sacCer3_chromosome_names,
    sacCer3_region_CNE1,
):
    patched_fn1.return_value = sacCer3_chromosome_names
    patched_fn2.return_value = sacCer3_region_CNE1
    patched_fn3.return_value = pickle.load(
        open(os.path.join(data_folder, "sacCer3_chrI_II_IX_itrees.pkl"), "rb")
    )
    genome_structure = get_genome_structure(organism="sacCer3", bam_filepath=bam_file)
    region = genome_structure.parse_regions("CNE1")[0]
    results = genome_structure.query(
        region,
        enzyme="cas9",
        min_specificity=0.46,
        as_dataframe=True,
        legacy_ordering=True,
        bam_filepath=bam_file,
    )
    old_results = load_saved_data(
        os.path.join(data_folder, "query_CNE1_min_specificity.json")
    )
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results["specificity"], results["specificity"]))
    assert np.all(
        np.isclose(old_results["cutting-efficiency"], results["cutting-efficiency"])
    )
    assert np.all(old_results["sequence"] == results["sequence"])
    assert np.all(old_results["start"] == results["start"])
    assert np.all(old_results["end"] == results["end"])

    assert_equal_offtargets(old_results, results)


@patch("guidescanpy.flask.core.genome.get_chromosome_interval_trees")
@patch("guidescanpy.flask.core.parser.create_region_query")
@patch("guidescanpy.flask.core.genome.get_chromosome_names")
def test_genome_structure_query_CNE1_min_cutting_efficiency(
    patched_fn1,
    patched_fn2,
    patched_fn3,
    data_folder,
    bam_file,
    sacCer3_chromosome_names,
    sacCer3_region_CNE1,
):
    patched_fn1.return_value = sacCer3_chromosome_names
    patched_fn2.return_value = sacCer3_region_CNE1
    patched_fn3.return_value = pickle.load(
        open(os.path.join(data_folder, "sacCer3_chrI_II_IX_itrees.pkl"), "rb")
    )
    genome_structure = get_genome_structure(organism="sacCer3", bam_filepath=bam_file)
    region = genome_structure.parse_regions("CNE1")[0]
    results = genome_structure.query(
        region,
        enzyme="cas9",
        min_ce=0.3,
        as_dataframe=True,
        legacy_ordering=True,
        bam_filepath=bam_file,
    )
    old_results = load_saved_data(
        os.path.join(
            data_folder,
            "query_CNE1_min_cutting_efficiency.json",
        )
    )
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results["specificity"], results["specificity"]))
    assert np.all(
        np.isclose(old_results["cutting-efficiency"], results["cutting-efficiency"])
    )
    assert np.all(old_results["sequence"] == results["sequence"])
    assert np.all(old_results["start"] == results["start"])
    assert np.all(old_results["end"] == results["end"])

    assert_equal_offtargets(old_results, results)


@patch("guidescanpy.flask.core.genome.get_chromosome_interval_trees")
@patch("guidescanpy.flask.core.parser.create_region_query")
@patch("guidescanpy.flask.core.genome.get_chromosome_names")
def test_genome_structure_query_offtarget_on_scaffold(
    patched_fn1,
    patched_fn2,
    patched_fn3,
    data_folder,
    bam_file,
    sacCer3_chromosome_names,
    sacCer3_region_CNE1,
):
    patched_fn1.return_value = sacCer3_chromosome_names
    patched_fn2.return_value = sacCer3_region_CNE1
    patched_fn3.return_value = pickle.load(
        open(os.path.join(data_folder, "sacCer3_chrI_II_IX_itrees.pkl"), "rb")
    )
    genome_structure = get_genome_structure(organism="sacCer3", bam_filepath=bam_file)
    region = genome_structure.parse_regions("chrIX:202231-202253")[0]
    results = genome_structure.query(
        region,
        enzyme="cas9",
        as_dataframe=True,
        legacy_ordering=True,
        bam_filepath=bam_file,
    )
    old_results = load_saved_data(
        os.path.join(data_folder, "query_offtarget_on_scaffold.json")
    )
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results["specificity"], results["specificity"]))
    assert np.all(
        np.isclose(old_results["cutting-efficiency"], results["cutting-efficiency"])
    )
    assert np.all(old_results["sequence"] == results["sequence"])
    assert np.all(old_results["start"] == results["start"])
    assert np.all(old_results["end"] == results["end"])

    assert_equal_offtargets(old_results, results)
