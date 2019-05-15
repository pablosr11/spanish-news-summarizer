from datetime import datetime
from app import db

class Article(db.Model):
 
    id = db.Column(db.Integer, primary_key=True)
    newspaper = db.Column(db.String)
    link = db.Column(db.String, unique=True)
    headline = db.Column(db.String)
    subheadline = db.Column(db.String)
    author = db.Column(db.String)
    article_date = db.Column(db.String)
    n_comments = db.Column(db.Integer)
    raw_text = db.Column(db.String)
    term_freq = db.Column(db.JSON) 
    nlp_analysed = db.Column(db.Boolean)
    labels = db.Column(db.JSON)
    categories = db.Column(db.JSON)
    last_scrape_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    votes = db.Column(db.Integer, default=0)
    nlp = db.relationship('Article_NLP', backref='article', lazy='dynamic')
    comments = db.relationship('Article_Comments', backref='article')

    def __repr__(self):
        return f'<Article {self.headline}>'


class Words(db.Model): #WORD_REPO

    id = db.Column(db.Integer, primary_key=True)
    word_stemm = db.Column(db.String, index=True, unique=True)
    word_raw = db.Column(db.String)
    articles_with_word = db.Column(db.Integer)
    total_occurences = db.Column(db.Integer)
    idf = db.Column(db.Float)

    def __repr__(self):
            return f'<Words {self.word_stemm}>'

class Article_NLP(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), unique=True)
    ranked_sentences = db.Column(db.PickleType)
    top_words = db.Column(db.PickleType)
    short_summary = db.Column(db.String)
    score = db.Column(db.Float, index=True)

    def __repr__(self):
        return f'<Article_NLP {self.short_summary}>'
    

class Article_Comments(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    text = db.Column(db.String)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    parent_id = db.Column(db.Integer) # if no value, comment- if reply, id of comment
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))

    def __repr__(self):
        return f'<Article_Comments {self.text}>'


"""
db.session.add(Article(headline='blablabla', link='/kjh/jjjj/klkl/', newspaper='www.poma.com', author='pablo', article_date='22-01-22'))
db.session.add(Article(headline='jeusito come en el cine', link='/deporte/jjjj', newspaper='www.poliesteruni.com', author='joselito', article_date='21-01-22'))
db.session.add(Article_NLP(article_id=1, score=9, short_summary='me lo como to'))
db.session.add(Article_NLP(article_id=2, score=4, short_summary='me lo como to segundo art'))
db.session.add(Article_Comments(username='joselito', text='wawawaw first comment', article_id=1))
db.session.add(Article_Comments(username='anonimo', text='wawawaw first comment', article_id=1, parent_id=1))
db.session.add(Article_Comments(username='joselito', text='wawawaw first comment', article_id=2))
db.session.add(Article_Comments(username='anonym', text='wawawawNOT the one', article_id=2, parent_id=3))
db.session.add(Article_Comments(username='joselito3', text='tf is this', article_id=2, parent_id=3))
db.session.add(Article_Comments(username='originator', text='un shijuajua', article_id=1, parent_id=4))
db.session.commit()
"""