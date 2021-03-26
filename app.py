import model

@app.route('/')
def root():
    return render_template('index.html', plot=model.get_plot(cnt=50))


@app.route('/posts')
def posts():
    return render_template('posts.html', posts=model.get_posts())


@app.route('/post/<id>')
def post(id):
    return render_template('post.html', post=model.get_post(id))


@app.route('/wordcloud')
def wordcloud():
    return render_template('wordcloud.html', plot=model.get_cloud_of_words())