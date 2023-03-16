from guidescan.flask.db import create_gene_symbol_query, get_chromosome_names


def test_create_gene_symbol_query_Mct2():
    # Get chromosome + position data for a gene
    results = create_gene_symbol_query('Mct2', 'mm10')
    assert results['entrez_id'] == 20503
    assert results['gene_symbol'] == 'Mct2'
    assert results['start_pos'] == 125219270
    assert results['end_pos'] == 125389586
    assert results['sense'] is False
    assert results['name'] == '10'
    assert results['accession'] == 'NC_000076.6'


def test_create_gene_symbol_query_Rad51():
    # Get chromosome + position data for a gene
    results = create_gene_symbol_query('Rad51', 'mm10')
    assert results['entrez_id'] == 19361
    assert results['gene_symbol'] == 'Rad51'
    assert results['start_pos'] == 119112814
    assert results['end_pos'] == 119136073
    assert results['sense'] is True
    assert results['name'] == '2'
    assert results['accession'] == 'NC_000068.7'


def test_create_gene_symbol_query_no_results():
    results = create_gene_symbol_query('Mct42', 'mm10')  # no such gene for mm10 organism
    assert results is None


def test_get_chromosome_names():
    results = get_chromosome_names('mm10')
    assert len(results) == 21
    assert results['NC_000068.7'] == '2'
    assert results['NC_000074.6'] == '8'
