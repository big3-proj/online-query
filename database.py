from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

pjdir = os.path.abspath(os.path.dirname(__file__))
# Create a Flask APP
app = Flask(__name__)
app.url_map.strict_slaskes = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(pjdir, 'data.sqlite')
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(12), unique=True, nullable=False)
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    pushes = db.relationship('Push', backref='user', lazy='dynamic')
    def __init__(self, uid):
        self.uid = uid

    def __repr__(self):
        return f'{self.uid}'
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(50))
    content = db.Column(db.Text)
    datetime = db.Column(db.String(25))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    pushes = db.relationship('Push', backref='post', lazy='dynamic')
    def __init__(self, pid, title, content, datetime):
        self.pid = pid
        self.title = title
        self.content = content
        self.datetime = datetime
    def __repr__(self):
        return f'{self.pid}'

class Push(db.Model):
    __tablename__ = 'pushes'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.String(25))
    content = db.Column(db.Text())
    floor = db.Column(db.Integer)
    usesr_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    def __init__(self, content, datetime, floor):
        self.content = content
        self.datetime = datetime
        self.floor = floor
