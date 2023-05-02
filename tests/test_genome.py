import os.path
import time
import urllib
import json
import numpy as np
import pandas as pd

from guidescanpy.flask.core.genome import get_genome_structure
from guidescanpy import config


def clj(organism, enzyme, query, filter_annotated=False, mode='within', **kwargs):
    filter_annotated = 'true' if filter_annotated else 'false'
    url = f'http://guidescan.com/backend/query?organism={organism}&enzyme={enzyme}&query-text={query}&filter-annotated={filter_annotated}&mode={mode}'
    for key, val in kwargs.items():
        key = key.replace('_', '-')
        url += f'&{key}={val}'

    r = urllib.request.urlopen(url)
    data = json.loads(r.read().decode('utf-8'))
    job_id = data['job-id']
    time.sleep(5)
    url = f'http://guidescan.com/backend/job/result/json/{job_id}?type=all&key={{}}'
    r = urllib.request.urlopen(url)
    data = json.loads(r.read().decode('utf-8'))
    return pd.DataFrame(data[0][1])


def test_genome_structure():
    genome_structure = get_genome_structure(organism='sacCer3')

    genome = genome_structure.genome
    assert genome[0][0:3] == (230218, 813184, 316620)
    assert genome[1][0:3] == ('NC_001133.9', 'NC_001134.8', 'NC_001135.5')
    assert np.allclose(genome_structure.absolute_genome[0:4], [0, 230218, 1043402, 1360022])
    assert genome_structure.off_target_delim == -12157106


def test_genome_structure_parse_CNE1():
    genome_structure = get_genome_structure(organism='sacCer3')
    region = genome_structure.parse_region('CNE1')
    assert region['region-name'] == 'CNE1'
    assert region['chromosome-name'] == 'I'
    assert region['coords'] == ('NC_001133.9', 37464, 38972)


def test_genome_structure_query_manual():
    genome_structure = get_genome_structure(organism='sacCer3')
    # manually selected region on chr2 for CNE1 gene
    results = genome_structure.query('NC_001133.9', 37464, 38972, enzyme='cas9')
    assert len(results) == 150


def test_genome_structure_query_CNE1():
    genome_structure = get_genome_structure(organism='sacCer3')
    results = genome_structure.query('CNE1', enzyme='cas9', as_dataframe=True)

    old_results = clj(organism='sacCer3', enzyme='cas9', query='CNE1')
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results['specificity'], results['specificity']))
    assert np.all(np.isclose(old_results['cutting-efficiency'], results['cutting-efficiency']))
    assert np.all(old_results['sequence'] == results['sequence'])
    assert np.all(old_results['start'] == results['start'])
    assert np.all(old_results['end'] == results['end'])

    assert np.all(old_results['off-targets'] == results['off-targets'])


def test_genome_structure_query_manual_filter_annotated():
    genome_structure = get_genome_structure(organism='sacCer3')
    results = genome_structure.query('chrII:5000-10000', enzyme='cas9', filter_annotated=True, as_dataframe=True)

    old_results = clj(organism='sacCer3', enzyme='cas9', query='chrII:5000-10000', filter_annotated=True)
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results['specificity'], results['specificity']))
    assert np.all(np.isclose(old_results['cutting-efficiency'], results['cutting-efficiency']))
    assert np.all(old_results['sequence'] == results['sequence'])
    assert np.all(old_results['start'] == results['start'])
    assert np.all(old_results['end'] == results['end'])

    assert np.all(old_results['off-targets'] == results['off-targets'])


def test_genome_structure_query_CNE1_min_specificity():
    genome_structure = get_genome_structure(organism='sacCer3')
    results = genome_structure.query('CNE1', enzyme='cas9', min_specificity=0.46, as_dataframe=True)

    old_results = clj(organism='sacCer3', enzyme='cas9', query='CNE1', s_bounds_l=0.46, s_bounds_u=1.0)
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results['specificity'], results['specificity']))
    assert np.all(np.isclose(old_results['cutting-efficiency'], results['cutting-efficiency']))
    assert np.all(old_results['sequence'] == results['sequence'])
    assert np.all(old_results['start'] == results['start'])
    assert np.all(old_results['end'] == results['end'])

    assert np.all(old_results['off-targets'] == results['off-targets'])


def test_genome_structure_query_CNE1_min_cutting_efficiency():
    genome_structure = get_genome_structure(organism='sacCer3')
    results = genome_structure.query('CNE1', enzyme='cas9', min_ce=0.3, as_dataframe=True)

    old_results = clj(organism='sacCer3', enzyme='cas9', query='CNE1', ce_bounds_l=0.3, ce_bounds_u=1.0)
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results['specificity'], results['specificity']))
    assert np.all(np.isclose(old_results['cutting-efficiency'], results['cutting-efficiency']))
    assert np.all(old_results['sequence'] == results['sequence'])
    assert np.all(old_results['start'] == results['start'])
    assert np.all(old_results['end'] == results['end'])

    assert np.all(old_results['off-targets'] == results['off-targets'])


def test_genome_structure_query_offtarget_on_scaffold():
    genome_structure = get_genome_structure(organism='sacCer3')
    results = genome_structure.query('chrIX:202231-202253', enzyme='cas9', as_dataframe=True)

    old_results = clj(organism='sacCer3', enzyme='cas9', query='chrIX:202231-202253')
    assert len(results) == len(old_results)
    assert np.all(np.isclose(old_results['specificity'], results['specificity']))
    assert np.all(np.isclose(old_results['cutting-efficiency'], results['cutting-efficiency']))
    assert np.all(old_results['sequence'] == results['sequence'])
    assert np.all(old_results['start'] == results['start'])
    assert np.all(old_results['end'] == results['end'])

    assert np.all(old_results['off-targets'] == results['off-targets'])