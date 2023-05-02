from intervaltree import Interval
from guidescanpy.flask.db import chromosome_interval_trees as interval_trees


def test_interval_tree_exists():
    assert "NC_001134.8" in interval_trees


def test_interval_tree_no_overlap():
    interval_tree = interval_trees["NC_001134.8"]
    query_interval = Interval(6_000, 7_000)
    # no interval for this chromosome is between 6k-7k in position
    assert not interval_tree.overlaps(query_interval)


def test_interval_tree_overlap():
    interval_tree = interval_trees["NC_001134.8"]
    query_interval = Interval(5_000, 10_000)
    # some intervals for this chromosome are between 5k-10k in position
    assert interval_tree.overlaps(query_interval)


def test_interval_tree_overlap_products():
    interval_tree = interval_trees["NC_001134.8"]
    overlaps = interval_tree[5_000:10_000]
    # 4 interval trees (hence 4 annotated exon products) are within position 5k-10k
    assert len(overlaps) == 4
