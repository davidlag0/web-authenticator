'''
Auth Blueprint
'''

from flask import Blueprint

auth_blueprint = Blueprint('auth', __name__)

# Routes are imported only after the Blueprint is fully initialized.
from . import routes