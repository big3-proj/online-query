import pandas as pd
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
    uid = db.Column(db.String(12), unique=True, nullable=False, primary_key=True)
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
    pid = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.Text)
    datetime = db.Column(db.DateTime)
    ip = db.Column(db.Text)
    user_id = db.Column(db.String(12), db.ForeignKey('users.uid'))
    pushes = db.relationship('Push', backref='post', lazy='dynamic')
    def __init__(self, pid, title, content, dt, ip=''):
        self.pid = pid
        self.title = title
        self.content = content
        self.datetime = datetime.strptime(dt, '%a %b %d %H:%M:%S %Y')
        self.ip = ip
    def __repr__(self):
        return f'{self.pid}'
    def info(self):
        pushes = [{
            'pushContent': push.content,
            'pushIpdatetime': push.datetime,
            'pushTag': '',
            'pushAuthorUid': push.user_id,
        } for push in self.pushes]
        return {
            'articlePid': self.pid,
            'articleTitle': self.title,
            'authorUid': self.user_id,
            'board': 'Gossiping',
            'content': self.content,
            'date': self.datetime,
            'ip': self.ip,
            'messages': pushes,
        }


class Push(db.Model):
    __tablename__ = 'pushes'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(1))
    content = db.Column(db.Text())
    datetime = db.Column(db.DateTime)
    floor = db.Column(db.Integer)
    ip = db.Column(db.Text)
    user_id = db.Column(db.String(12), db.ForeignKey('users.uid'))
    post_id = db.Column(db.String(20), db.ForeignKey('posts.pid'))
    def __init__(self, tag, content, dt, floor, ip=''):
        self.tag = tag
        self.content = content
        self.datetime = datetime.strptime(dt, '%Y/%m/%d %H:%M')
        self.floor = floor
        self.ip = ip
    def __repr__(self):
        return f'{self.post_id}, floor: {self.floor}'


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(12), db.ForeignKey('users.uid'))
    content = db.Column(db.Text())
    pos = db.Column(db.String(20))
    day_count = db.Column(db.Text())
    __table_args__ = (db.Index('uid_word', 'user_id', 'content'),)
    def __init__(self, content, pos):
        self.content = content
        self.pos = pos
        self.day_count = ','.join(map(str, [0]*367))
    def __repr__(self):
        return f'{self.content}, day_count: {self.day_count}'


def get_posts(offset=0, count=20):
    return list(map(lambda p: p.info(), Post.query.offset(offset).limit(count).all()))


def get_post(pid):
    return Post.query.get(pid).info()


def get_user_pushes_hour(user):
    pushes = user.pushes.all()
    posts = user.posts.all()
    activate_datetime = []
    # minute in datetime is irrelevant, same hour pushes in a day is viewed as one activity
    if pushes: activate_datetime = set([f'{push.datetime.month},{push.datetime.day},{push.datetime.hour}' for push in pushes])
    if posts: activate_datetime = set([f'{post.datetime.month},{post.datetime.day},{post.datetime.hour}' for post in posts] + list(activate_datetime))
    activate_hours = map(
            lambda dt: int(dt.split(',')[2]),
            activate_datetime
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
    

def get_plot(cnt=None, users=None):
    if not users:
        users = User.query.limit(cnt).all()
    else:
        users = list(filter(None, [User.query.get(user_id) for user_id in users]))
    return get_tsne_of_users(users)


def get_cloud_of_words(user_id):
    words = User.query.get(user_id).words.all()
    pos_filter = ['V.$', 'Na', 'Nb', 'Nc', 'Neu']
    regexes = re.compile('|'.join('(?:{0})'.format(r) for r in pos_filter))
    words_filtered = list(filter(lambda w: 
                                    bool(re.match(regexes, w.pos))
                                    and 'http' not in w.content
                                    , words))

    data = [{'word': w.content, 'freq': int(w.day_count.split(',')[0])} for w in words_filtered]
    return data


def get_ridgeline_of_word(users_id, word):
    '''
    return a dictionary: {
        [user_id]: a 365-element list where element is an int indicating the 
                   freq of word in that day
        ,...
    }
    '''
    data = {}
    for user_id in users_id:
        user_word = Word.query.filter_by(user_id=user_id, content=word).first()
        if user_word:
            day_count = user_word.day_count
            data[user_id] = day_count.split(',')[1:]
        else:
            data[user_id] = [0] * 365
    return data
