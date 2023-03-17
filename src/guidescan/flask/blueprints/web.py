import logging
import json
from importlib.resources import read_text
from flask import Blueprint, request, render_template, send_file, session, abort, redirect, url_for


bp = Blueprint('web', __name__)
logger = logging.getLogger(__name__)


@bp.route('/')
def index():
    return redirect(url_for('web.grna_design'))


@bp.route('/grna_design')
def grna_design():
    return render_template('grna_design.html')


@bp.route('/gene_targeting_library')
def gene_targeting_library():
    return render_template('gene_targeting_library.html')


@bp.route('/grna_sequence_search')
def grna_sequence_search():
    return render_template('grna_sequence_search.html')


@bp.route('/about')
def about():
    return render_template('about.html')


@bp.route('/downloads')
def downloads():
    return render_template('downloads.html')


@bp.route('/contact')
def contact():
    return render_template('contact.html')

