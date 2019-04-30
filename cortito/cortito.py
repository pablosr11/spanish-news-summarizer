"""
 Copyright 2019 Pablo Sanderson Ramos
"""

"""
streamline whole process every X hours (2,6?) and refactor/correct mistakes
multithread to make it faster (web scraping)
separate calculatetf in two functions
dont keep articles with less than X words
TESTING build word working as expected? no duplication, good aditions etc?
TESTING idf working?
#still need to clean » symbols and HTML from text


"""
import sys#look for files outsite directory as well
sys.path.append('../')

import math
import news_scraper as ns #import scraping functionality
import nlp_scorer as nlp #nlp functionality
import datetime #get scraping time
import pickle
from sqlalchemy import between
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

    print('Starting Data Scraper--')

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

            #skip articles with less than 100 words
            if len(data['raw_text'].split()) < 100:
                print('\tLess than 100 words')
                continue

            #get term freq for document
            # tf(stemword:term_freq) and words[(stem,raw)]
            tf,_= nlp.calculate_tf(data['raw_text']) 

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
                term_freq = tf,
                nlp_analysed = False,
                last_scrape_date = datetime.datetime.now()
            )

            session.add(article)
            session.commit()

def build_word_repo():
    """
    Goes through every article, calculate its tf, scores each
    word and store all data in database.
    """

    print('Building Word Repo---')

    docs_repo = session.query(Article)

    #right now iterates over everything, look for a way to filter it out (old files no need to redo?)
    for article in docs_repo:

        text_id = article.id
        text = article.raw_text #text document

        art = session.query(Article).filter(Article.id == text_id).first()

        #if already analysed, skip it
        if art.nlp_analysed: 
            continue

        # tf(stemword:term_freq) and words[(stem,raw)]
        # get list of words in doc to iterate over
        _,word_list = nlp.calculate_tf(text) 

        
        #keep track of words added to word repo to only add it once per document
        # a word appearing eight in a doc means total_occ +8 but articleswithword +1
        words_included = set()

        for word_tuple in word_list:

            w_stemm = word_tuple[0]
            w_raw = word_tuple[1]

            #check if word already stored
            raw = session.query(Word_Repo).filter(Word_Repo.word_stemm == w_stemm).first()

            # add total occurrences every time, but only once per doc for articles with word
            # if word is already in database, modify its counters
            if raw:

                #fail check
                if raw.articles_with_word > docs_repo.count():
                    sys.exit(f'TFIDF Error - More articles with word than articles.\
                     \nWord: {raw.word_stemm}\
                     \nTotal docs:  {docs_repo.count()}\
                     \nDocs with Word: {raw.articles_with_word}')


                #if we haven't store this document word, update counter and add it to tracker
                if w_stemm not in words_included:
                    raw.articles_with_word += 1
                    words_included.add(w_stemm)

                raw.total_occurences += 1
                session.commit()
                continue

            # if word not in repo, create it and commit to database
            word_repo = Word_Repo(
                word_stemm = w_stemm,
                word_raw = w_raw,
                articles_with_word = 1,
                total_occurences = 1,
                idf = 1.0
            )
            session.add(word_repo)
            session.commit()
        
        #change flag after analysing and commit
        art.nlp_analysed = True
        session.commit()
        
    pass 

def idf_updater():
    """
    Update each word IDF. Goes through word_repo updating it and commiting to db
    """

    print('Updating IDFs---')

    total_docs = session.query(Article).count()
    words_repo = session.query(Word_Repo)#.filter(Word_Repo.id<5)

    for word in words_repo:

        word_id = word.idf
        word_docs_with_word = word.articles_with_word

        word.idf = nlp.calculate_word_idf(total_docs,word_docs_with_word)
        session.commit()

    pass

def nlp_magic():
    """
    for every article, calculate tfidf, rank its sentences, get top words and store a small summary
    """

    print('Ranking Sentences---')

    articles = session.query(Article)#.filter(between(Article.id,2,3))
    words = session.query(Word_Repo)

    for article in articles:
        
        #article's words tf-idf scores.
        doc_tfidf = {}

        for word, term_freq in article.term_freq.items():

            #get idf of the current word we are iterating
            w_idf = words.filter(Word_Repo.word_stemm == word).first().idf
        
            if w_idf < 0 or term_freq < 0:
                print('(INVALID) Negative IDF or TF', article.link)

            #store new tfidf score in local dict
            doc_tfidf[word] = nlp.calculate_tfidf(term_freq,w_idf)

        #rank sentences
        ranked_sentences = nlp.rank_sentences(article.raw_text,doc_tfidf)

        #top 5 words
        top_words = nlp.top_words(article.raw_text,doc_tfidf)

        #keep summary to the smallest
        summary = nlp.summarizer(article.raw_text,doc_tfidf,0.99)

        #persist data in database
        article_nlp = Article_NLP(
            article_id = article.id,
            ranked_sentences = ranked_sentences,
            top_words = top_words,
            short_summary = summary
        )

        session.add(article_nlp)
        session.commit()


if __name__ == "__main__":
    #data_scraper(10)
    #build_word_repo()
    #idf_updater()
    nlp_magic()
    print('-----Cortito.py')