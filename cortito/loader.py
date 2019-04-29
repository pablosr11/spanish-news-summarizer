"""

    Copyright 2019 Pablo Sanderson Ramos

todo:   change all repo to pickle dict,list data
        include latest scraped time in article (datetime sqlalchemy)
    
"""

#https://docs.sqlalchemy.org/en/13/orm/tutorial.html
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, PickleType, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship

db_engine = create_engine('sqlite:///cortito.db', echo=False)
Base = declarative_base()

class Article(Base):
    #missing labels element
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    newspaper = Column(String)
    link = Column(String, unique = True)
    headline = Column(String)
    subheadline = Column(String)
    author = Column(String)
    article_date = Column(String)
    n_comments = Column(Integer)
    main_cat = Column(String)
    sub_cat = Column(String)
    raw_text = Column(String)
    nlp_analysed = Column(Boolean)
    last_scrape_date = Column(DateTime)

    article_nlp = relationship('Article_NLP', uselist=False, back_populates='article')

class Word_Repo(Base):
    __tablename__ = 'word_repo'

    id = Column(Integer, primary_key=True)
    word_stemm = Column(String, unique=True)
    word_raw = Column(String)
    articles_with_word = Column(Integer)
    total_occurences = Column(Integer)
    idf = Column(Float)

class Article_NLP(Base):
    __tablename__ = 'article_nlp'

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('article.id'), unique=True)
    term_freq = Column(PickleType) #move to other table as they keep varying with new idfs
    ranked_sentences = Column(PickleType)
    top_words = Column(PickleType)
    short_summary = Column(String)

    article = relationship('Article', back_populates='article_nlp')


Base.metadata.create_all(db_engine)


    
if __name__ == "__main__":

    print('-----Loader.py')
