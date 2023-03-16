from flask import json


def test_info(app):
    response = app.test_client().get('/info/supported')
    assert response.mimetype == 'application/json'
    data = json.loads(response.data)
    assert 'version' in data       # The version of this app
    assert 'cli-version' in data   # Guidescan CLI Version
    assert 'available' in data     # A list of dicts with enzyme/organism/file keys


def test_query(app):
    # For the mm10 organism and Rad51 gene, find hits for the Mct2 enzyme
    # query-text can be a gene symbol, a chromosome name, or an entrez id
    response = app.test_client().get('/query?organism=mm10&enzyme=Mct2&query-text=Rad51')
    assert response.mimetype == 'application/json'
    data = json.loads(response.data)