"""

    Copyright 2019 Pablo Sanderson Ramos

    
"""
#https://docs.sqlalchemy.org/en/13/orm/tutorial.html
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, PickleType, ForeignKey

engine = create_engine('sqlite:///main.db', echo=False, convert_unicode = True)
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = Session.query_property()

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
        term_freq = Column(PickleType) #move to other table as they keep varying with new idfs
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
    ranked_sentences = Column(PickleType)
    top_words = Column(PickleType)
    short_summary = Column(String)
    score = Column(Float)

    article = relationship('Article', back_populates='article_nlp')


Base.metadata.create_all(engine)


if __name__ == "__main__":
    print('-----Loader.py')
