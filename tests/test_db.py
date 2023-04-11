from guidescanpy.flask.db import create_region_query, get_chromosome_names



def test_create_region_query_CNE1():
    # Get chromosome + position data for a gene
    results = create_region_query('sacCer3', region='CNE1')
    assert results['entrez_id'] == 851241
    assert results['region_name'] == 'CNE1'
    assert results['start_pos'] == 37464
    assert results['end_pos'] == 38972
    assert results['sense'] is True
    assert results['chromosome_name'] == 'I'
    assert results['chromosome_accession'] == 'NC_001133.9'


def test_create_region_query_no_results():
    results = create_region_query('sacCer3', region='CNE42')  # no such gene for sacCer3 organism
    assert results is None


def test_create_region_query_entrez_id():
    # Get chromosome + position data for an entrez ID
    results = create_region_query('sacCer3', region='852343')
    assert results['entrez_id'] == 852343
    assert results['region_name'] == 'YRO2'
    assert results['start_pos'] == 343101
    assert results['end_pos'] == 344135
    assert results['sense'] is True
    assert results['chromosome_name'] == 'II'
    assert results['chromosome_accession'] == 'NC_001134.8'


def test_get_chromosome_names():
    results = get_chromosome_names('sacCer3')
    assert len(results) == 16
    assert results['NC_001140.6'] == 'chrVIII'
    assert results['NC_001147.6'] == 'chrXV'
