import pandas as pd
import itertools
import numpy as np
import json
from datetime import datetime
from functools import reduce
from collections import Counter
from sklearn.manifold import TSNE
from os import listdir
from app import db
import re

db.create_all()
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(12), unique=True, nullable=False)
    ips = db.Column(db.Text)
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    pushes = db.relationship('Push', backref='user', lazy='dynamic')
    words = db.relationship('Word', backref='user', lazy='dynamic')
    def __init__(self, uid, ip=''):
        self.uid = uid
        self.ips = ip
    def __repr__(self):
        return f'{self.uid}'


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(50))
    content = db.Column(db.Text)
    datetime = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    pushes = db.relationship('Push', backref='post', lazy='dynamic')
    def __init__(self, pid, title, content, dt):
        self.pid = pid
        self.title = title
        self.content = content
        self.datetime = datetime.strptime(dt, '%a %b %d %H:%M:%S %Y')
    def __repr__(self):
        return f'{self.pid}'


class Push(db.Model):
    __tablename__ = 'pushes'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    content = db.Column(db.Text())
    floor = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    def __init__(self, content, dt, floor):
        self.content = content
        self.datetime = datetime.strptime(dt, '%Y/%m/%d %H:%M')
        self.floor = floor
    def __repr__(self):
        return f'{self.post_id}, floor: {self.floor}'


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    content = db.Column(db.Text())
    pos = db.Column(db.String(20))
    day_count = db.Column(db.Text())
    def __init__(self, content, pos):
        self.content = content
        self.pos = pos
        self.day_count = ','.join(map(str, [0]*367))
    def __repr__(self):
        return f'{self.content}, day_count: {self.day_count}'


# load posts
with open('./posts.json') as f:
    posts = json.load(f)


def get_posts():
    return posts


def get_post(id):
    return posts[id]


def get_user_pushes_hour(user):
    pushes = Push.query.with_parent(user).all()
    posts = Post.query.with_parent(user).all()
    activate_datetime = []
    # minute in datetime is irrelevant, same hour pushes in a day is viewed as one activity
    if pushes: activate_datetime = set([f'{push.datetime.month},{push.datetime.day},{push.datetime.hour}' for push in pushes])
    if posts: activate_datetime = set([f'{post.datetime.month},{post.datetime.day},{post.datetime.hour}' for post in posts] + activate_datetime)
    activate_hours = filter(None, map(
            lambda dt: int(dt.split(',')[2]),
            activate_datetime
        )
    )
    counter = Counter(activate_hours)
    return [counter.get(i, 0) for i in range(24)]


def get_activity_label(activity):
    label = ['midnight', 'morning', 'afternoon', 'evening']
    section = [sum(activity[i:i+6]) for i in range(0, 24, 6)]
    return label[section.index(max(section))]


def get_tsne_of_users(users):
    users_activities = [get_user_pushes_hour(u) for u in users]
    users_activity_label = [get_activity_label(activity) for activity in users_activities]
    # t-SNE
    X = np.array(users_activities)
    X_embedded = TSNE(n_components=2).fit_transform(X).tolist()
    plots = []
    for i in range(len(users)):
        plots.append({
            'id': users[i].uid,
            'coord': X_embedded[i],
            'label': users_activity_label[i],
            'activities': users_activities[i],
        })
    return plots
    

def get_plot(cnt=None):
    users = User.query.limit(cnt).all()
    return get_tsne_of_users(users)


def get_cloud_of_words(user_id):
    words = Word.query.filter_by(user_id=user_id).all()
    pos_filter = ['FW', '^V', 'Na', 'Nb', 'Nc', 'Neu']
    regexes = re.compile('|'.join('(?:{0})'.format(r) for r in pos_filter))
    words_filtered = list(filter(lambda w: bool(re.match(regexes, w.pos)), words))

    data = [{'word': w.content, 'freq': w.day_count[0]} for w in words_filtered]
    return data


def get_ridgeline_of_word(users_id, word):
    data = {}
    users_word = Word.query.filter_by(content=word)
    for user_id in users_id:
        day_count = users_word.filter_by(user_id=user_id).first().day_count
        data[user_id] = day_count.split(',')[1:]
    return data
