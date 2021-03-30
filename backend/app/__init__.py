from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from os import path

pjdir = path.abspath(path.dirname(__file__))
# Create a Flask APP
app = Flask(__name__)
app.url_map.strict_slaskes = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + path.join(pjdir, '../data.sqlite')
db = SQLAlchemy(app)

from . import views