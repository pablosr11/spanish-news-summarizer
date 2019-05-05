from flask import Flask
from flask import render_template
from sqlalchemy import desc
from .database import Session, Article, Article_NLP

app = Flask(__name__)

@app.route('/')
def website():
    articles = Article.query.order_by(desc(Article.last_scrape_date)).limit(35)
    #points not corresponding to articles, join on article.id == article_nlp.article_id and order the same
    nlps = Article_NLP.query.all()
    return render_template('rss/index.html', articles=zip(articles,nlps))


@app.teardown_appcontext
def cleanup(resp_or_exc):
    Session.remove()
