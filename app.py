from flask import Flask, render_template
import model

# Create a Flask APP
app = Flask(__name__)
app.url_map.strict_slaskes = False


@app.route('/')
def root():
    return render_template('index.html', plot=model.get_plot())


@app.route('/posts')
def posts():
    return render_template('posts.html', posts=model.get_posts())


@app.route('/post/<id>')
def post(id):
    return render_template('post.html', post=model.get_post(id), plot=model.get_plot_of_post(id))


@app.route('/wordcloud')
def wordcloud():
    return render_template('wordcloud.html', plot=model.get_plot_of_words())