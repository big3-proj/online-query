import pandas as pd
import itertools
import numpy as np
import json
from datetime import datetime
from functools import reduce
from collections import Counter
from sklearn.manifold import TSNE
from os import listdir


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

def get_plot_of_words():
    u = 'jma306'
    with open(f'./users/{u}.json') as f:
        user = json.load(f)
    data = [{'word': k, 'freq': v} for k, v in user['words_freq'][0].items()]
    return data
