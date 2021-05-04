from flask import Flask, request
from utils import *
from app import app
import model
@app.route('/')
def root():
    return 'hello'


@app.route('/analyze')
def analyze():
    return HTTPResponse('here you are.', data=model.get_plot(cnt=100))


@app.route('/posts')
def get_posts():
    return HTTPResponse('here you are.', data=model.get_posts())


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
