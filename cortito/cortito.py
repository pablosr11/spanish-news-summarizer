"""
 Copyright 2019 Pablo Sanderson Ramos
"""

"""
prepare NLP and WORD table (and connect it to article)
multithread to make it faster
dont keep articles with less than X words
test it, is build word working as expect it=


"""
import sys#look for files outsite directory as well
sys.path.append('../')

import news_scraper as ns #import scraping functionality
import nlp_scorer as nlp #nlp functionality
import datetime #get scraping time
import pickle
import settings #import list of newspapers
from loader import Article, Word_Repo, Article_NLP, db_engine
from sqlalchemy.orm import sessionmaker

#initiate session to talk to the database
Session = sessionmaker(bind=db_engine)
session = Session()


def data_scraper(how_many=500):
    """
    For each newspaper, collect data for every news article in its website and store it in database
    optional parameter for how many links to scrape
    """

    for outlet in settings.OUTLETS:
 
        # get all news links for each outlet
        news_link = ns.get_links(outlet.strip(),how_many)

        for link in news_link:

            #if its already in database, skip it
            if session.query(Article).filter(Article.link == link).first():
                continue

            print(link)

            # get all text, headlines etc from each article and store it in DB
            full_link = outlet+link
            data = ns.extract_data(full_link)

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
                raw_text = data['raw_text'],
                nlp_analysed = False,
                last_scrape_date = datetime.datetime.now()
            )

            session.add(article)
            session.commit()

def build_word_repo():
    """
    Given a text document, calculate its tf, tfidf, rank its sentences, score each
    word and store all data in database.
    """

    docs_repo = session.query(Article).filter(Article.id<5)

    #right now iterates over everything, look for a way to filter it out (old files no need to redo?)
    for article in docs_repo:

        text_id = article.id
        text = article.raw_text #text document

        #keep track of which word are included in the word repo
        words_included = []

        art = session.query(Article).filter(Article.id == text_id).first()

        if art.nlp_analysed: #if already analysed, skip it
            continue

        # tf(stemword:term_freq) and words[(stem,raw)]
        tf,word_list = nlp.calculate_tf(text) 

        #store tf and words in respective repos
        #keep track of analysed links to dont store value twice

        article_nlp = Article_NLP(
            article_id = article.id,
            term_freq = tf,
            ranked_sentences = {},
            top_words = {},
            short_summary = ''
        )
        session.add(article_nlp)
        session.commit()

        
        for word_tuple in word_list:

            #check if word already stored
            raw = session.query(Word_Repo).filter(Word_Repo.word_stemm == word_tuple[0]).first()

            # add total occurrences every time, but only once per doc for articles with word
            if raw: #check if word already stored
                raw.total_occurences += 1
                if word_tuple[0] not in words_included:
                    raw.articles_with_word += 1
                    words_included.append(word_tuple[0])
                session.commit()
                continue

            word_repo = Word_Repo(
                word_stemm = word_tuple[0],
                word_raw = word_tuple[1],
                articles_with_word = 1,
                total_occurences = 1,
                idf = 1.0
            )
            session.add(word_repo)
            session.commit()
        
        #change flag after analysing and commit
        art.nlp_analysed = True
        session.commit()
        
        #print([x for x in words])
        
    pass 


if __name__ == "__main__":
    #data_scraper()
    build_word_repo()
    print('-----Cortito.py')