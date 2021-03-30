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
    word_freq = db.Column(db.Text)
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    pushes = db.relationship('Push', backref='user', lazy='dynamic')
    def __init__(self, uid):
        self.uid = uid
        self.word_freq = ''

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    def __init__(self, content, datetime, floor):
        self.content = content
        self.datetime = datetime
        self.floor = floor
    def __repr__(self):
        return f'{self.content}'


# load posts
with open('./posts.json') as f:
    posts = json.load(f)


def get_posts():
    return posts


def get_post(id):
    return posts[id]


def get_user_pushes_hour(user):
    pushes = Push.query.with_parent(user).all()
    # minute in datetime is irrelevant, same hour pushes in a day is viewed as one activity
    pushes_datetime = set([push.datetime.split(':')[0] for push in pushes])
    pushes_hours = filter(None, map(
            lambda dt: None if len(dt.split(' ')) < 2 else int(dt.split(' ')[1]),
            pushes_datetime
        )
    )
    counter = Counter(pushes_hours)
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
    users = User.query.all()
    return get_tsne_of_users(users)


def get_cloud_of_words():
    user = 'go190214'
    wq_list = User.query.filter_by(uid = user).first().word_freq.split(';')
    wq_pos = [w for w in [wq.split(',') for wq in wq_list]]

    pos_filter = ['FW', '^V', 'Na', 'Nb', 'Nc', 'Neu']
    regexes = re.compile('|'.join('(?:{0})'.format(r) for r in pos_filter))
    wq = list(filter(lambda wq: bool(re.match(regexes, wq[1])), wq_pos))

    data = [{'word': w[0], 'freq': w[2]} for w in wq]
    return data
