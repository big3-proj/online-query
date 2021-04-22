# -*- coding= utf-8 -*-
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
import itertools
from ckiptagger import WS, POS
from tqdm import tqdm
import sys
from datetime import datetime
import json

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


def tag_word(content):
    # tagger
    ws = WS('ckipdata')
    pos = POS('ckipdata')
    ws_list = ws(content)
    pos_list = pos(ws_list)
    del ws
    del pos
    # flatten and merge
    ws_list = list(itertools.chain(*ws_list))
    pos_list = list(itertools.chain(*pos_list))
    wp_list = [[ws_list[i], pos_list[i]] for i in range(len(ws_list))]

    return wp_list


def tag_sentence(day_of_year, day_user_sentence):
    for uid, sentence in tqdm(day_user_sentence.items(), desc=f'Tagging sentence'):
        wp_list = tag_word(sentence)
        for w, p in wp_list:
            word = Word.query.filter_by(content=w, user_id=uid).first()
            if word is None: word = Word(w, p)
            word_day_count = list(map(int, word.day_count.split(',')))
            word_day_count[0] += 1 # sum
            word_day_count[day_of_year] += 1
            word.day_count = ','.join(map(str, word_day_count))
            user = User.query.filter_by(uid=uid).first()
            user.words.append(word)
        db.session.add(user)
        db.session.commit()


def parse_data():
    day_user_sentence = {}
    day = -1
    for a in tqdm(data['articles'][:3], desc=f'Parsing articles'):
        # remove nickname
        author_id = a['author'].split()[0]

        # add posts to DB
        post = Post(a['article_id'], a['article_title'], a['content'] , a['date'])
        if not day_user_sentence:
            day = int(post.datetime.strftime('%j'))
        if int(post.datetime.strftime('%j')) != day:
            day_user_sentence = {}
            tag_sentence(day, day_user_sentence)
        
        author = User.query.filter_by(uid=author_id).first()
        if author is None:
            author = User(author_id, a['ip'])
        elif not len(author.ips):
            author.ips = a['ip']
        else:
            author.ips = ';'.join(author.ips.split(';').append(a['ip']))
        author.posts.append(post)
        db.session.add(author)
        db.session.commit()
        if author_id not in day_user_sentence: day_user_sentence[author_id] = []
        day_user_sentence[author_id].append(a['content'])

        # add pushes to DB
        f = 0
        for m in a['messages']:
            push = Push(m['push_content'], post.datetime.strftime('%Y')+'/'+m['push_ipdatetime'], f)
            pusher = User.query.filter_by(uid=m['push_userid']).first()
            if pusher is None: pusher = User(m['push_userid'])
            pusher.pushes.append(push)
            post.pushes.append(push)
            if m['push_userid'] not in day_user_sentence: day_user_sentence[m['push_userid']] = []
            day_user_sentence[m['push_userid']].append(m['push_content'])
            f += 1
        
        db.session.add(post)
        db.session.commit()
    tag_sentence(day, day_user_sentence)

if __name__ == '__main__':
    data = pd.read_json(f'{sys.argv[1]}')
    db.create_all()

    parse_data()