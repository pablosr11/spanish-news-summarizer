"""
 Copyright 2019 Pablo Sanderson Ramos
"""

"""

deploy web/script
cleanup github, write desc etc

Build test cases for main func.
    check updates are implemented
General refactor
    scrape comments properly (now mostly "")
    improve cleaning func ( symbols and HTML from text)
    separate calculate tf in two functs
Future devs
    add forum (with summary?)
    add upvotes
    ranking : count in upvotes, visits.
    multithread


"""

import sys#look for files outsite directory as well
sys.path.append('../')

import math
import news_scraper as ns #import scraping functionality
import nlp_scorer as nlp #nlp functionality

import pickle
import time
import traceback
from sqlalchemy import between
import settings #import list of newspapers
from database import Article, Article_NLP, Word_Repo
from database import Session
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta


#initiate session to talk to the database
session = Session()

# set of updated words (included in new articles). dont delete
word_update_idf = set()

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

        print(newspaper)
 
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
            if len(data['raw_text'].split()) < settings.MINIMUM_WORDS_ARTICLE:
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
                last_scrape_date = datetime.now()
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

    #only work on articles that are in time to make it on board
    last_x_hours = (datetime.now()-timedelta(hours= settings.TIME_ON_BOARD))

    docs_repo = session.query(Article).filter(Article.last_scrape_date>last_x_hours)

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
            word_update_idf.add(w_stemm)

            #check if word already stored
            raw = session.query(Word_Repo).filter(Word_Repo.word_stemm == w_stemm).first()

            # add total occurrences every time, but only once per doc for articles with word
            # if word is already in database, modify its counters
            if raw:

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
    words_repo = session.query(Word_Repo).filter(Word_Repo.word_stemm.in_(word_update_idf))
    total_docs = session.query(Article).count()

    for word in words_repo:

        word_docs_with_word = word.articles_with_word
        idf_counter += 1

        word.idf = nlp.calculate_word_idf(total_docs,word_docs_with_word)
        session.commit()

    print(f'[IDF] Word\'s updated: {idf_counter}')

    #reset set of words updated

def rank_docs():
    """
    for every article, calculate tfidf, rank its sentences, get top words and store a small summary
    """

    print('-- Ranking Sentences')

    #tracker for final print statement
    articles_updated = 0

    # only update articles of the last cicle
    last_x_hours = (datetime.now()-timedelta(hours= settings.TIME_ON_BOARD))
   
    articles = session.query(Article).filter(Article.last_scrape_date>last_x_hours)
    words = session.query(Word_Repo)

    articles_to_add = []

    for article in articles:

        # check if words updated are included in the articles,
        #  if not, skip the article (dont update its summary etc)
        if len(word_update_idf & set(article.term_freq)) < settings.UPDATED_WORDS:
            continue
        
        #tracker
        articles_updated += 1

        #build tf-idf dict
        doc_tfidf = nlp.build_tfidf_dict(article,words,Word_Repo)
       
        #rank sentences
        ranked_sentences = nlp.rank_sentences(article.raw_text,doc_tfidf)

        #top 5 words
        top_words = nlp.top_words(article.raw_text,doc_tfidf)

        #keep summary to the smallest (function will round up to avoid empty strings)
        summary = nlp.summarizer(article.raw_text,doc_tfidf,settings.SUMMARIZATION_POINTS)

        #sum the score out of its sentences
        art_score = sum([x[1] for x in ranked_sentences])

        #add record to list of articles
        articles_to_add.append([article,ranked_sentences, top_words, summary, art_score])

        

    #separate adding to db from building articles
    for art in articles_to_add:

        art_id = art[0].id
        ranked_sentences = art[1]
        top_words = art[2]
        short_summary = art[3]
        score = art[4]

        #query existing articles_nlp with this article.id
        art_in_db = session.query(Article_NLP).filter(Article_NLP.article_id == art_id).first()

        #if item already in database, update numbers and continue, no need to create
        if art_in_db:
            art_in_db.ranked_sentences = ranked_sentences
            art_in_db.top_words = top_words
            art_in_db.short_summary = short_summary
            art_in_db.score = score
            #session.commit() #should I commit once outside loop?
            continue


        #if not in db, create new one
        article_nlp = Article_NLP(
            article_id = art_id,
            ranked_sentences = ranked_sentences,
            top_words = top_words,
            short_summary = short_summary,
            score = score
        )

        #change flag and add to database
        art[0].nlp_analysed = True
        session.add(article_nlp)

    session.commit()
    
    #empty tracker of new words added
    word_update_idf.clear()

    print(f'[NLP] Articles updated: {articles_updated}')
    



if __name__ == "__main__":
    while True:
        print(f"{time.ctime()}: Starting cycle")
        try:
            data_scraper()
            build_word_repo()
            idf_updater()
            rank_docs()
        except KeyboardInterrupt:
            print("Exiting....")
            sys.exit(1)
        except Exception as exc:
            print("Error in:", sys.exc_info()[0])
            traceback.print_exc()
        else:
            print(f"{time.ctime()}: Successfully finished")
        time.sleep(settings.WAITING_TIME)