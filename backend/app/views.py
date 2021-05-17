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
    return HTTPResponse('here you are.', data=model.get_posts())


@app.route('/post/<id>')
def post(id):
    return HTTPResponse('here you are.', data=model.get_post(id))


@app.route('/wordcloud/<user_id>')
def wordcloud(user_id):
    return HTTPResponse('here you are.', data=model.get_cloud_of_words(user_id))
