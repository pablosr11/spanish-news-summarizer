"""
 Copyright 2019 Pablo Sanderson Ramos
"""

"""

prepare NLP and WORD table (and connect it to article)



"""

import news_scraper as ns #import scraping functionality

import sys#look for files outsite directory as well
sys.path.append('../')
import settings #import list of newspapers
from loader import Article, db_engine
from sqlalchemy.orm import sessionmaker


"""
class Article(Base):
    #missing labels element
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    newspaper = Column(String)
    link = Column(String, unique = True)
    headline = Column(String)
    subheadline = Column(String)
    author = Column(String)
    article_date = Column(DateTime)
    n_comments = Column(Integer)
    main_category = Column(String)
    sub_category = Column(String)
    raw_text = Column(String)
    term_freq = Column(PickleType)
    ranked_sentences = Column(PickleType)
    top_words = Column(PickleType)
"""

Session = sessionmaker(bind=db_engine)
session = Session()

def data_scraper(how_many):

    for outlet in settings.OUTLETS:

        for news_link in ns.get_links(outlet.strip(),how_many):
            
            

            #if its already in database, skip it
            if session.query(Article).filter(Article.link == news_link).first():
                continue

            print(news_link)
            #check link is not already in database
            link = outlet+news_link
            data = ns.extract_data(link)

            article = Article(
                newspaper=data['newspaper'],
                link = data['news_link'],
                headline = data['headline'],
                subheadline = data['subhead'],
                author = data['author'],
                article_date = data['date'],
                n_comments = data['n_comments'],
                main_cat = data['main_cat'],
                sub_cat = data['sub_cat'],
                raw_text = data['raw_text']
            )

            session.add(article)
            session.commit()

            

if __name__ == "__main__":
    print(data_scraper(20))