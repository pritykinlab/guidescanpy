from guidescan.flask.db import create_region_query, get_chromosome_names


def test_create_region_query_Mct2():
    # Get chromosome + position data for a gene
    results = create_region_query('mm10', region='Mct2')
    assert results['entrez_id'] == 20503
    assert results['region_name'] == 'Mct2'
    assert results['start_pos'] == 125219270
    assert results['end_pos'] == 125389586
    assert results['sense'] is False
    assert results['chromosome_name'] == '10'
    assert results['chromosome_accession'] == 'NC_000076.6'


def test_create_region_query_Rad51():
    results = create_region_query('mm10', region='Rad51')
    assert results['entrez_id'] == 19361
    assert results['region_name'] == 'Rad51'
    assert results['start_pos'] == 119112814
    assert results['end_pos'] == 119136073
    assert results['sense'] is True
    assert results['chromosome_name'] == '2'
    assert results['chromosome_accession'] == 'NC_000068.7'


def test_create_region_query_no_results():
    results = create_region_query('mm10', region='Mct42')  # no such gene for mm10 organism
    assert results is None


def test_create_region_query_entrez_id():
    # Get chromosome + position data for an entrez ID
    results = create_region_query('mm10', region='19361')
    assert results['entrez_id'] == 19361
    assert results['region_name'] == 'Rad51'
    assert results['start_pos'] == 119112814
    assert results['end_pos'] == 119136073
    assert results['sense'] is True
    assert results['chromosome_name'] == '2'
    assert results['chromosome_accession'] == 'NC_000068.7'


def test_get_chromosome_names():
    results = get_chromosome_names('mm10')
    assert len(results) == 21
    assert results['NC_000068.7'] == 'chr2'
    assert results['NC_000074.6'] == 'chr8'
