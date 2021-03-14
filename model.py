import pandas as pd
import itertools
import numpy as np
import json
import re
from datetime import datetime
from functools import reduce
from collections import Counter
from sklearn.manifold import TSNE
from os import listdir
from ckiptagger import WS, POS


# load posts
with open('./posts.json') as f:
    posts = json.load(f)


def get_posts():
    return posts


def get_post(id):
    return posts[id]


def get_user_pushes_hour(user):
    with open(f'./users/{user}.json') as f:
        user = json.load(f)
    pushes = user['pushes']
    # minute in datetime is irrelevant, same hour pushes in a day is viewed as one activity
    pushes_datetime = set([push['datetime'].split(':')[0] for push in pushes])
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
            'id': users[i],
            'coord': X_embedded[i],
            'label': users_activity_label[i],
            'activities': users_activities[i],
        })
    return plots
    

def get_plot(cnt=None):
    json_files = list(filter(lambda x: x[-5:] == '.json', listdir('./users')))
    users = list(map(lambda x: x[:-5], json_files))[:cnt]
    return get_tsne_of_users(users)


def get_cloud_of_user_word(id):
    with open(f'users/{id}.json') as f:
        user = json.load(f)
    user_wordlist = [p['content'] for p in user['pushes']]
    
    # tagger
    ws = WS('ckipdata')
    pos = POS('ckipdata')
    ws_list = ws(user_wordlist)
    pos_list = pos(ws_list)
    del ws
    del pos
    
    # flatten and merge
    ws_list = list(itertools.chain(*ws_list))
    pos_list = list(itertools.chain(*pos_list))
    wp_list = [[ws_list[i], pos_list[i]] for i in range(len(ws_list))]
    
    # keywords filter
    pos_filter = ['FW', '^V', 'Na', 'Nb', 'Nc', 'Neu']
    regexes = re.compile('|'.join('(?:{0})'.format(r) for r in pos_filter))
    wp_list = list(filter(lambda wp: bool(re.match(regexes, wp[1])), wp_list))
    # remove URL
    ws_list = [wp[0] for wp in wp_list if not any(u in wp[0] for u in ['http', 'com/', 'imgur', 'jpg'])]
    
    word_sentence_occurence = [{'word': word, 'freq': ws_list.count(word)} for word in list(set(ws_list))]
    return word_sentence_occurence
    

def get_cloud_of_words():
    users = ['jma306']
    return [get_cloud_of_user_word(u) for u in users]
