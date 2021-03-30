from flask import Flask, render_template, request
from utils import *
from app import app
import model
@app.route('/')
def root():
    return 'hello'


@app.route('/analyze')
def analyze():
    return HTTPResponse('here you are.', data=model.get_plot(cnt=50))


@app.route('/posts')
def get_posts():
    return HTTPResponse('here you are.', data=model.get_posts())


@app.route('/post/<id>')
def post(id):
    return HTTPResponse('here you are.', data=model.get_post(id))


@app.route('/wordcloud')
def wordcloud():
    return HTTPResponse('here you are.', data=model.get_cloud_of_words())
    # return render_template('wordcloud.html', plot=model.get_cloud_of_words())
