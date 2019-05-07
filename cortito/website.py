from flask import Flask
from flask import render_template
from sqlalchemy import desc
import settings
from .database import Session, Article, Article_NLP
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def website():

    #create session to "talk" with database
    session = Session()

    # how many news do we show?
    n_articles = settings.ARTICLES_TO_SHOW

    # time difference now vs hours on board
    last_x_hours = (datetime.now()-timedelta(hours=settings.TIME_ON_BOARD))
    
    #give X number articles of the last X hours ordered by score
    articles = session.query(Article, Article_NLP, )\
        .filter(Article.last_scrape_date>last_x_hours,\
                Article.id==Article_NLP.article_id)\
        .order_by(desc(Article_NLP.score))\
        .limit(n_articles)

    return render_template('rss/index.html', articles=articles)

@app.teardown_appcontext
def cleanup(resp_or_exc):
    Session.remove()
