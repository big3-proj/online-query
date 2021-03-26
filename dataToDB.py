from database import *
import pandas as pd

db.create_all()
data = pd.read_json('../Gossiping-38819-38868.json')

for a in data['articles'][:2]:
    # remove nickname
    author_id = a['author'].split()[0]

    # add posts to DB
    post = Post(a['article_id'], a['article_title'], a['content'] , a['date'])
    author = User.query.filter_by(uid=author_id).first()
    if author is None: author = User(author_id)
    author.posts.append(post)
    db.session.add(author)
    db.session.commit()

    # add pushes to DB
    f = 0
    for m in a['messages']:
        push = Push(m['push_content'], m['push_ipdatetime'], f)
        pusher = User.query.filter_by(uid=m['push_userid']).first()
        if pusher is None: pusher = User(m['push_userid'])
        pusher.pushes.append(push)
        post.pushes.append(push)
        f += 1
    
    db.session.add(post)
    db.session.commit()