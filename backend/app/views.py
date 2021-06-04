from flask import Flask, request
from utils import *
from app import app
import model
@app.route('/')
def root():
    return 'hello'


@app.route('/analyze', methods=['POST'])
def analyze():
    payload = request.get_json()
    if 'users' in payload:
        users = payload['users']
    else:
        users = None
    return HTTPResponse('here you are.', data=model.get_plot(cnt=100, users=users))


@app.route('/posts')
def get_posts():
    offset = request.args.get('offset')
    count = request.args.get('count')
    return HTTPResponse('here you are.', data=model.get_posts(offset=offset, count=count))


@app.route('/post/<id>')
def post(id):
    return HTTPResponse('here you are.', data=model.get_post(id))


@app.route('/wordcloud/<user_id>')
def wordcloud(user_id):
    return HTTPResponse('here you are.', data=model.get_cloud_of_words(user_id))


@app.route('/ridgeline', methods=['POST'])
def ridgeline():
    payload = request.get_json()
    word = payload['word']
    users = payload['users']
    return HTTPResponse('here you are.', data=model.get_ridgeline_of_word(users, word))
