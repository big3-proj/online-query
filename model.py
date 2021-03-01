import pandas as pd
import itertools
import numpy as np
import json
from datetime import datetime
from functools import reduce
from collections import Counter
from sklearn.manifold import TSNE

filename = 'top_100_users_pushes.csv'

df = pd.read_csv(f'../segmentation/{filename}',
                 index_col='pusher_id', keep_default_na=False)
df = df.loc[df['push_tag'] != '']
art_df = pd.read_csv(
    f'../segmentation/{filename}', index_col='article_author', keep_default_na=False)
art_df = art_df.loc[art_df['pusher_id'] == '']
users = list(set(df.index))
art_users = list(set(art_df.index))

with open('./posts.json') as f:
    posts = json.load(f)

def parse_timestamp(push_timestamp):
    [date, time] = push_timestamp.split()
    time = datetime.strptime(time, '%H:%M:%S').hour
    return {'date': date, 'time': time}


def to_data(data):
    if len(data) == 2:
        return {'tag': data[0], **parse_timestamp(data[1])}
    return {'tag': '', **parse_timestamp(data[0])}


def get_activity(user):
    return list(map(to_data, df.loc[[user], ['push_tag', 'push_timestamp']].values.tolist()))


def get_art_activity(user):
    return list(map(to_data, art_df.loc[[user], ['article_timestamp']].values.tolist()))


activities = [get_activity(u) for u in users] + \
    [get_art_activity(u) for u in art_users]

# activity
# [
#     {
#       'tag': '噓',
#       'date': '2019-12-28',
#       'time': 18
#     },
#     ...
# ]


def get_online_activity(activity):
    return list(map(lambda x: json.loads(x), set((map(lambda x: json.dumps({'date': x['date'], 'time': x['time']}), activity)))))


# serialization is for unique the list, after encoding it we have to decode it
online_activities = [get_online_activity(a) for a in activities]


def get_online_times(activity):
    return Counter(a['time'] for a in activity)


online_activities = [[get_online_times(oa).get(
    i, 0) for i in range(24)] for oa in online_activities]


def get_plot():
    X = np.array(online_activities)
    X_embedded = TSNE(n_components=2).fit_transform(X)
    return X_embedded.tolist()


def get_posts():
    return posts


def get_post(id):
    return posts[id]


def get_plot_of_post(id):
    post = posts[id]
    commenters = list(map(lambda x: x['push_userid'], post['messages']))
    users = list(set([post['author_id']] + commenters))
    users_activities = []
    for u in users:
        with open(f'./users/{u}.json') as f:
            user = json.load(f)
        def parse_push(push):
            datetime = push['datetime'].split(' ')
            datetime[1] = datetime[1].split(':')[0]
            return { 'tag': '', 'date': datetime[0], 'time': datetime[1] }
        users_activities.append(list(map(parse_push, user['pushes'])))
    users_online_activities = [get_online_activity(ua) for ua in users_activities]
    users_online_activities = [[get_online_times(oa).get(i, 0) for i in range(24)] for oa in users_online_activities]
    X = np.array(users_online_activities)
    X_embedded = TSNE(n_components=2).fit_transform(X)
    return X_embedded.tolist()
