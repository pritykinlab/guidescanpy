from flask import json


def test_info(app):
    response = app.test_client().get('/info/supported')
    assert response.mimetype == 'application/json'
    data = json.loads(response.data)
    assert 'version' in data       # The version of this app
    assert 'cli-version' in data   # Guidescan CLI Version
    assert 'available' in data     # A list of dicts with enzyme/organism/file keys


def test_query_gene_symbol(app):
    # For the sacCer3 organism and CNE1 gene, find hits for the cas9 enzyme
    # query-text can be a gene symbol, a chromosome region, or an entrez id
    response = app.test_client().get('/query?organism=sacCer3&enzyme=cas9&query-text=CNE1')
    assert response.mimetype == 'application/json'
    data = json.loads(response.data)
    assert len(data) == 1  # We passed in a single line in query-text, so we get a single result
    assert len(data[0]) == 150


def test_query_entrez_id(app):
    response = app.test_client().get('/query?organism=sacCer3&enzyme=cas9&query-text=852343')
    assert response.mimetype == 'application/json'
    data = json.loads(response.data)
    assert len(data) == 1
    assert len(data[0]) == 89


def test_query_chr(app):
    response = app.test_client().get('/query?organism=sacCer3&enzyme=cas9&query-text=chrIX:200000-320000')
    assert response.mimetype == 'application/json'
    data = json.loads(response.data)
    assert len(data) == 1
    assert len(data[0]) == 8655


def test_query_chr_bad(app):
    # No such chromosome - chrXX
    response = app.test_client().get('/query?organism=sacCer3&enzyme=cas9&query-text=chrXX:1000-2000')
    assert response.mimetype == 'application/json'
    data = json.loads(response.data)
    assert len(data) == 1
    assert len(data[0]) == 0


def test_query_chr_pos_bad(app):
    # Positions don't exist on chrV, which is length 576874
    response = app.test_client().get('/query?organism=sacCer3&enzyme=cas9&query-text=chrV:182113225-182113225')
    assert response.mimetype == 'application/json'
    data = json.loads(response.data)
    assert len(data) == 1
    assert len(data[0]) == 0