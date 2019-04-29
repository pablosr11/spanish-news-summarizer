"""from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker

db_engine = create_engine('sqlite:///cortito.db', echo=False)
Base = declarative_base()

class Listing(Base):
    
    #A table to store data on craigslist listings.
    

    __tablename__ = 'listings'
    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    created = Column(DateTime)
    geotag = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    name = Column(String)
    price = Column(Float)
    location = Column(String)
    cl_id = Column(Integer, unique=True)
    area = Column(String)
    bart_stop = Column(String)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()"""

"""
todo:   change all repo to pickle dict,list data
        move rank sentence,
            top words
            term freq
            to arcicle nlp table
"""

#https://docs.sqlalchemy.org/en/13/orm/tutorial.html
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, PickleType
from sqlalchemy.orm import sessionmaker

db_engine = create_engine('sqlite:///cortito.db', echo=False)
Base = declarative_base()

class Article(Base):
    #missing labels element
    __tablename__ = 'articles'

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
    #term_freq = Column(PickleType) #move to other table as they keep varying with new idfs
    #ranked_sentences = Column(PickleType)
    #top_words = Column(PickleType)
    #last_scrape_date = Column(DateTime)
    #times_scraped = Column(Integer)

class Word_Repo(Base):
    __tablename__ = 'word_repo'

    id = Column(Integer, primary_key=True)
    word_stemm = Column(String)
    word_raw = Column(String)
    articles_with_word = Column(Integer)
    total_occurences = Column(Integer)
    idf = Column(Float)

class Article_NLP(Base):
    __tablename__ = 'article_nlp'

    id = Column(Integer, primary_key=True)


Base.metadata.create_all(db_engine)
#Session = sessionmaker(bind=db_engine)
#session = Session()



#a = session.query(Word_Repo).filter_by(word_stemm='hol').first()
#pablo = Article(newspaper='https://www.canarias7.es/',link='/politica/el-psoe-gana-las-elecciones-en-canarias-HY7122584')

#session.add(pablo)
#session.commit()

    
if __name__ == "__main__":
    
    #session.query(Word_Repo).delete()
    #session.commit()
    #for x in session.query(Article):
    #    print(x.id,x.newspaper)
    #a= session.query(Word_Repo).filter(Word_Repo.word_stemm == 'zurito').first()
    #a.word_stemm='muhalalalalalala'
    #session.commit()

    print('-----')
