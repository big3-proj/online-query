# -*- coding= utf-8 -*-
from app import *
import pandas as pd
from ckiptagger import WS, POS
import itertools

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

db.create_all()
data = pd.read_json('../Gossiping-38819-38868.json')

new_user_sentence = {}
# parse data to database
for a in data['articles'][1:2]:
    # remove nickname
    author_id = a['author'].split()[0]

    # add posts to DB
    post = Post(a['article_id'], a['article_title'], a['content'] , a['date'])
    author = User.query.filter_by(uid=author_id).first()
    if author is None: author = User(author_id)
    author.posts.append(post)
    db.session.add(author)
    db.session.commit()
    if author_id not in new_user_sentence: new_user_sentence[author_id] = []
    new_user_sentence[author_id].append(a['content'])

    # add pushes to DB
    f = 0
    for m in a['messages']:
        push = Push(m['push_content'], m['push_ipdatetime'], f)
        pusher = User.query.filter_by(uid=m['push_userid']).first()
        if pusher is None: pusher = User(m['push_userid'])
        pusher.pushes.append(push)
        post.pushes.append(push)
        if m['push_userid'] not in new_user_sentence: new_user_sentence[m['push_userid']] = []
        new_user_sentence[m['push_userid']].append(m['push_content'])
        f += 1
    
    db.session.add(post)
    db.session.commit()

# tag the sentence
for k, v in new_user_sentence.items():
    wp_list = tag_word(v)
    user = User.query.filter_by(uid=k).first()
    if user.word_freq:
        word_freq_dict = {w[0]: [w[1], int(w[2])] for w in [wq.split(',') for wq in user.word_freq.split(';')]}
    else: word_freq_dict = {}
    for wp in wp_list:
        if wp[0] not in word_freq_dict: word_freq_dict[wp[0]] = [wp[1], 0]
        word_freq_dict[wp[0]][1] += 1

    user.word_freq = ';'.join(k+','+v[0]+','+str(v[1]) for k, v in word_freq_dict.items())
    
    db.session.add(user)
    db.session.commit()