import os.path
import time
import urllib
import json
import numpy as np
import pandas as pd

from guidescanpy.flask.core.genome import get_genome_structure
from guidescanpy import config


def clj(organism, enzyme, query, filter_annotated=False, mode='within'):
    filter_annotated = 'true' if filter_annotated else 'false'
    url = f'http://localhost:8000/query?organism={organism}&enzyme={enzyme}&query-text={query}&filter-annotated={filter_annotated}&mode={mode}'
    r = urllib.request.urlopen(url)
    data = json.loads(r.read().decode('utf-8'))
    job_id = data['job-id']
    time.sleep(5)
    url = f'http://localhost:8000/job/result/json/{job_id}?type=all&key={{}}'
    r = urllib.request.urlopen(url)
    data = json.loads(r.read().decode('utf-8'))
    return pd.DataFrame(data[0][1])


def test_genome_structure():
    genome_structure = get_genome_structure(organism='mm10')

    genome = genome_structure.genome
    assert genome[0][0:3] == (195471971, 169725, 241735)
    assert genome[1][0:3] == ('NC_000067.6', 'NT_166280.1', 'NT_166281.1')
    assert np.allclose(genome_structure.absolute_genome[0:4], [0, 195471971, 195641696, 195883431])
    assert genome_structure.off_target_delim == -2818974549


def test_genome_structure_parse_Rad51():
    genome_structure = get_genome_structure(organism='mm10')
    region = genome_structure.parse_region('Rad51')
    assert region['region-name'] == 'Rad51'
    assert region['chromosome-name'] == '2'
    assert region['coords'] == ('NC_000068.7', 119112814, 119136073)


def test_genome_structure_query_manual():
    genome_structure = get_genome_structure(organism='mm10')
    # manually selected region on chr2 for Rad1 gene
    results = genome_structure.query('NC_000068.7', 119112814, 119136073, enzyme='cas9')
    assert len(results) == 1430


def test_genome_structure_query_Rad51():
    genome_structure = get_genome_structure(organism='mm10')
    results = genome_structure.query('Rad51', enzyme='cas9', as_dataframe=True)

    old_results = clj(organism='mm10', enzyme='cas9', query='Rad51')
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results['specificity'], results['specificity']))
    assert np.all(np.isclose(old_results['cutting-efficiency'], results['cutting-efficiency']))
    assert np.all(old_results['sequence'] == results['sequence'])
    assert np.all(old_results['start'] == results['start'])
    assert np.all(old_results['end'] == results['end'])

    assert np.all(old_results['off-targets'] == results['off-targets'])


def test_genome_structure_query_bug1():
    genome_structure = get_genome_structure(organism='mm10')
    results = genome_structure.query('chr2:119127007-119127029', enzyme='cas9', as_dataframe=True)

    old_results = clj(organism='mm10', enzyme='cas9', query='chr2:119127007-119127029')
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results['specificity'], results['specificity']))
    assert np.all(np.isclose(old_results['cutting-efficiency'], results['cutting-efficiency']))
    assert np.all(old_results['sequence'] == results['sequence'])
    assert np.all(old_results['start'] == results['start'])
    assert np.all(old_results['end'] == results['end'])

    assert np.all(old_results['off-targets'] == results['off-targets'])
