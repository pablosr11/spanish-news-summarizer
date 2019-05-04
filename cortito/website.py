from flask import Flask
from .database import Session, Article

app = Flask(__name__)

@app.route('/')
def website():
    a = [x.headline for x in Article.query.filter(Article.id>5, Article.id <15)]
    for x in a:
        return x
    return f'hello darling, {a}'


@app.teardown_appcontext
def cleanup(resp_or_exc):
    Session.remove()
