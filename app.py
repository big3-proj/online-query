from flask import Flask, render_template

# Create a Flask APP
app = Flask(__name__)
app.url_map.strict_slaskes = False


@app.route('/')
def root():
    return render_template('root/index.html', msg='hello, world')
