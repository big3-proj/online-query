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


# serialization is for unique the list, after encoding it we have to decode it
def get_online_activity(activity):
    return list(map(lambda x: json.loads(x), set((map(lambda x: json.dumps({'date': x['date'], 'time': x['time']}), activity)))))


def get_online_times(activity):
    return Counter(a['time'] for a in activity)


def get_online_label(activity):
    label = ['midnight', 'morning', 'afternoon', 'evening']
    section = [sum(activity[i:i+6]) for i in range(0, 24, 6)]
    return label[section.index(max(section))]


def get_posts():
    return posts


def get_post(id):
    return posts[id]


def get_plot_of_users(users):
    users_activities = []
    valid_users = []
    for u in users:
        with open(f'./users/{u}.json') as f:
            user = json.load(f)
        def parse_push(push):
            datetime = push['datetime'].split(' ')
            try:
                datetime[1] = datetime[1].split(':')[0]
                return { 'tag': '', 'date': datetime[0], 'time': int(datetime[1]) }
            except:
                return None
        users_activities.append([x for x in list(map(parse_push, user['pushes'])) if x is not None])
        valid_users.append(u)
    users_online_activities = [get_online_activity(ua) for ua in users_activities]
    users_online_activities = [[get_online_times(oa).get(i, 0) for i in range(24)] for oa in users_online_activities]
    users_online_label = [get_online_label(u) for u in users_online_activities]
    X = np.array(users_online_activities)
    X_embedded = TSNE(n_components=2).fit_transform(X).tolist()
    for i in range(len(X_embedded)):
        X_embedded[i].append(users_online_label[i])
        X_embedded[i].append(valid_users[i])
    return X_embedded


def get_plot_of_post(id):
    post = posts[id]
    commenters = list(map(lambda x: x['push_userid'], post['messages']))
    users = list(set([post['author_id']] + commenters))
    return get_plot_of_users(users)
    

def get_plot():
    json_files = list(filter(lambda x: x[-5:] == '.json', listdir('./users')))
    users_ids = list(map(lambda x: x[:-5], json_files))
    return get_plot_of_users(users_ids[:50])
