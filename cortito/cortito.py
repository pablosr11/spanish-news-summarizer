"""
 Copyright 2019 Pablo Sanderson Ramos
"""

"""
summaries not working (all "" )
Refactor/correct mistakes

deploy to server
quick website with flask
multithread to make it faster (web scraping)
separate calculatetf in two functions
dont keep articles with less than X words
TESTING build word working as expected? no duplication, good aditions etc?
TESTING idf working?
testing sets
#still need to clean » symbols and HTML from text

"""

import sys#look for files outsite directory as well
sys.path.append('../')

import math
import news_scraper as ns #import scraping functionality
import nlp_scorer as nlp #nlp functionality
import datetime #get scraping time
import pickle
import time
import traceback
from sqlalchemy import between
import settings #import list of newspapers
from loader import Article, Word_Repo, Article_NLP, db_engine
from sqlalchemy.orm import sessionmaker


#initiate session to talk to the database
Session = sessionmaker(bind=db_engine)
session = Session()

# set of updated words (included in new articles). dont delete
ww = set()

def data_scraper(how_many=500):
    """
    For each newspaper, collect data for every news article in its website and store it in database
    optional parameter for how many links to scrape
    """

    print('-- Starting Data Scraper')

    #trackers of before/after numbers of docs and link activity
    before_docs = session.query(Article).count()
    links_scraped, links_skipped = 0, 0

    for newspaper in settings.OUTLETS:
 
        # get all news links for each newspaper
        news_link = ns.get_links(newspaper.strip(),how_many)

        for link in news_link:

            #if its already in database, skip it
            if session.query(Article).filter(Article.link == link).first():
                continue

            links_scraped+=1

            # get all text, headlines etc from each article and store it in DB
            full_link = newspaper+link
            data = ns.extract_data(full_link)

            #skip articles with less than 100 words
            if len(data['raw_text'].split()) < 100:
                links_skipped += 1
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

    after_docs = session.query(Article).count()

    print(f'[Articles] Before: {before_docs} - After: {after_docs} - New ones: {after_docs-before_docs}\
        \n[Articles] Links Scrapped: {links_scraped} - Skipped: {links_skipped}')


def build_word_repo():
    """
    Goes through every article, calculate its tf, scores each
    word and store all data in database.
    """

    print('-- Building Word Repo')
    before_words = session.query(Word_Repo).count()
    articles_analysed = 0
    total_word_occurrences = 0

    docs_repo = session.query(Article)

    #right now iterates over everything, look for a way to filter it out (old files no need to redo?)
    for article in docs_repo:

        articles_analysed +=1

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

            #add words to tracker to update idfs only of these words (Avoid long loops)
            ww.add(w_stemm)

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

                total_word_occurrences += 1
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
        
    after_words = session.query(Word_Repo).count()
    print(f'[Words] Before: {before_words} - After: {after_words} - New ones: {after_words-before_words}\
        \n[Words] Articles analysed : {articles_analysed}, Word Occurrences added: {total_word_occurrences}')

def idf_updater():
    """
    Update each word IDF. Goes through word_repo updating it and commiting to db
    """

    print('-- Updating IDFs')
    idf_counter = 0

    # only update idfs of new added words
    words_repo = session.query(Article).filter(Article.id.in_(ww))
    total_docs = session.query(Article).count()

    for word in words_repo:

        word_docs_with_word = word.articles_with_word
        idf_counter += 1

        word.idf = nlp.calculate_word_idf(total_docs,word_docs_with_word)
        session.commit()

    print(f'[IDF] Word\'s updated: {idf_counter}')

    #reset set of words updated

def nlp_magic():
    """
    for every article, calculate tfidf, rank its sentences, get top words and store a small summary
    """

    print('-- Ranking Sentences')

    #tracker for final print statement
    articles_updated = 0

    articles = session.query(Article)
    words = session.query(Word_Repo)

    
    for article in articles:

        # check if words updated are included in the articles, if not, skip the article
        if len(ww & set(article.term_freq)) < 1:
            continue
        
        #article's words tf-idf scores.
        doc_tfidf = {}

        #tracker
        articles_updated += 1

        for word, term_freq in article.term_freq.items():

            #get idf of the current word we are iterating
            w_idf = words.filter(Word_Repo.word_stemm == word).first().idf
        
            #fail check as both idf and tf have to be positive
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


        art_nlp = session.query(Article_NLP).filter(Article_NLP.article_id == article.id).first()

        #if item already in database, update numbers and continue, no need to create
        if art_nlp:
            art_nlp.ranked_sentences = ranked_sentences
            art_nlp.top_words = top_words
            art_nlp.short_summary = summary
            session.commit()
            continue


        #persist data in database
        article_nlp = Article_NLP(
            article_id = article.id,
            ranked_sentences = ranked_sentences,
            top_words = top_words,
            short_summary = summary
        )

        session.add(article_nlp)
        session.commit()
    
    #clear set with words updated
    ww.clear()

    print(f'[NLP] Articles updated: {articles_updated}')

if __name__ == "__main__":
    while True:
        print(f"{time.ctime()}: Starting cycle")
        try:
            data_scraper()
            build_word_repo()
            idf_updater()
            nlp_magic()
        except KeyboardInterrupt:
            print("Exiting....")
            sys.exit(1)
        except Exception as exc:
            print("Error in:", sys.exc_info()[0])
            traceback.print_exc()
        else:
            print(f"{time.ctime()}: Successfully finished")
        time.sleep(settings.WAITING_TIME)