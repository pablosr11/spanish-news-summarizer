"""
 Copyright 2019 Pablo Sanderson Ramos
"""

"""

follow tutorial
vote arrow not showing
testing
concurrent web scraping etc
in global menu show X hours ago
only 1 vote 
ordenar por nuevos, votos, puntuacion, comentarios.
laprovincia, el dia pocas noticias
make te scraper reliable (make sure code 200, proxies etc - notify when break)
multithread
cleanup github etc
Build test cases for main func.
    check updates are implemented
add europapress/etc 
"""

from app import db
##add here the whole process
from app import app
from app.models import Article, Words, Article_NLP
from sqlalchemy import exists
import requests #download websites
from bs4 import BeautifulSoup #scrape websites
from urllib.parse import urlparse #parse the ufo
from datetime import datetime, timedelta
import collections
import string #remove punctuation with string.translate
from nltk.stem.snowball import SnowballStemmer #ciudades -> ciudad
from nltk.corpus import stopwords #for spanish stopwords
import re
import random
import math
import time

def do_work():

    #track of n of articles before adding more
    before_art = Article.query.count()
    
    # iterate through newspapers defined in config
    for url in app.config['NEWSPAPERS']:

        print('Started Task', url)

        #keep track of new words to shorten idf updates
        new_words = set()

        #get news_link from website
        links = get_links(url)

        print('Extracting data')

        for link in links:

            #skip if link in db
            if Article.query.filter(Article.link == link).first():
                continue

            data = extract_data(url+link)

            #skip if empty dictionary
            if not data:
                continue

            #calculate termfreq and store its term frequency
            tf = calculate_tf(data['raw_text'])
            data['term_freq'] = tf

            #persist article in database
            article = Article(
                newspaper = data['newspaper'],
                link = link,
                headline = data['headline'],
                subheadline = data['subhead'],
                author=data['author'],
                article_date=data['date'],
                n_comments=0,
                raw_text=data['raw_text'],
                term_freq=data['term_freq'],
                nlp_analysed=False,
                labels=data['labels'],
                categories=data['categories'],
                last_scrape_date=data['scrape_date'],
                votes=random.random()*40 #test it out
            )
            db.session.add(article)


            #update word repository with new documents
            #set to avoid counting a word twice 
            words_in_doc = set(data['term_freq'])

            #add words to word_repo
            for word in words_in_doc:

                #check if word is already in database, to either create or update it
                word_in_db = Words.query.filter(Words.word_stemm == word).first()

                # keep track of new words to only update
                # new words
                new_words.add(word)

                #create if new word, update articles and ocurrence if not
                if word_in_db:
                    #add 1 article appearance
                    word_in_db.articles_with_word += 1
                else:
                    word = Words(
                        word_stemm = word,
                        word_raw = '',
                        articles_with_word = 1,
                        total_occurences = 1,
                        idf = 1.0
                    )
                    db.session.add(word)
            
        # commit after looping through each article and
        # word to add in bulk (avoid half-baked commit)
        try:
            db.session.commit()
        except Exception as e:
            print('Couln\'t commit to DB', link, e)
            continue
        

        # after entering/updating the new words, and
        # added articles to db, calculate word idf and
        # rank documents

        # how many articles do we have in storage
        number_of_docs = Article.query.count()
        
        print('Updating IDF')

        # iterate through new words to update its idf
        # with new article appearances
        for word in new_words:
                
            w = Words.query.filter(Words.word_stemm==word).first()

            #update its idf with the article count and its #of appearances
            w.idf = calculate_word_idf(number_of_docs, w.articles_with_word)
            
        # commit updated idf to database
        # to be used in ranking of documents
        db.session.commit()

        
        print('Ranking documents')
    
        # query articles that havent been ranked before
        articles = Article.query.filter(Article.nlp_analysed==False)

        #after updating all words idf, update the article rankings
        for article in articles:

            #keep article text in variable for better readability
            doc_tfidf = {}
            text = article.raw_text

            for word, tf in article.term_freq.items():

                try:
                    w_idf = Words.query.filter(Words.word_stemm == word).first().idf
                except:
                    print(word)
                    continue

                #store new tfidf score in local dict
                doc_tfidf[word] = tf * w_idf

            ranked_sentences = rank_sentences(text, doc_tfidf)
            top_words = get_top_words(text,doc_tfidf)
            summary = summarizer(ranked_sentences,0.8)

            #sum the score out of its sentences
            art_score = sum([x[1] for x in ranked_sentences])

            # if already stored, update values. if not, create new
            nlp_in_database = Article_NLP.query.filter(Article_NLP.article_id == article.id).first()

            # if exist, update value and go to next article
            if nlp_in_database:
                nlp_in_database.short_summary = summary
                nlp_in_database.top_words = top_words
                nlp_in_database.score = art_score
                nlp_in_database.ranked_sentences = ranked_sentences 
                continue
    
            #if new, create and add to db
            article_nlp = Article_NLP(
                article_id = article.id,
                ranked_sentences = ranked_sentences,
                top_words = top_words,
                short_summary = summary,
                score = art_score
            )

            article.nlp_analysed = True
            db.session.add(article_nlp)

        #commit all changes to article_nlp
        db.session.commit()
        

    print('Completed. New Articles: ', Article.query.count()-before_art)

    print(f"SLEEPING FOR {app.config['SLEEP_TIME']/60} MINUTES")
    time.sleep(app.config['SLEEP_TIME'])

    
   
        

def get_links(url,n_links=5):
    """Given a news website, return its articles links. Identifies where links are depending on outlet"""

    # it doesnt get content that loads with JS - solution would query directly those urls
    # https://gohighbrow.com/scraping-javascript-heavy-websites/ not implemented

    parsed_url = urlparse(url)
    html = get_html(url) #get bs4 object

    links = [] #store news links

    # give parameters to scrape website depending on link
    if parsed_url.netloc == 'www.canarias7.es':
        links = [link.parent['href'] for link in html.find_all(['h2','h3','div'], attrs={'class':'headline'}) 
                if link.parent.has_attr('href')]

    if parsed_url.netloc == 'www.laprovincia.es':
        links = [link['href'] for link in html.find_all('a', attrs={'data-tipo':'noticia'})]

    if parsed_url.netloc == 'www.eldia.es':
        links = [link['href'] for link in html.find_all('a', attrs={'data-tipo':'noticia'})]
    
    if parsed_url.netloc == 'www.noticanarias.com':
        links = [link['href'] for link in html.find_all('a', attrs={'itemprop':'url'})]

    if parsed_url.netloc == 'www.canarias24horas.com':
        links = [link.findChildren('a')[0]['href'] for link in html.find_all('h4', attrs={'class':'nspHeader'})]
    
    if parsed_url.netloc == 'canariasnoticias.es':
        links = [link.find('a')['href'] for link in html.find_all(attrs={'class':'title'})]

    if parsed_url.netloc == 'www.sanborondon.info':
        links = [link.find('a')['href'] for link in html.find_all(attrs={'class':'nspHeader'})]

    if parsed_url.netloc == 'tribunadecanarias.es':
        links = [link.find('a')['href'] for link in html.find_all(attrs={'class':'ns2-title'})]

    if parsed_url.netloc == 'www.canariasdiario.com':
        links = [link['href'] for link in html.find_all(attrs={'itemprop':'mainEntityOfPage'})]

    if parsed_url.netloc == 'www.europapress.es':
        links = [link.find('a')['href'] for link in html.find_all(attrs={'itemprop':'headline'})]

    if parsed_url.netloc == 'www.efe.com':
        links = [link['href'] for link in html.find_all('a', attrs={'itemprop':'url'})]

    return links

def get_html(url):
    """Given URL, output BeautifulSoup object of html content"""

    raw_data = requests.get(url)
    html = BeautifulSoup(raw_data.content, 'lxml')

    return html

def extract_data(url):
    """Given news article URL, return a dictionary with its data """

    #author link?

    parsed_url = urlparse(url)
    html = get_html(url)

    if parsed_url.netloc == 'www.canarias7.es':
        try:
            text = html.find(attrs={'itemprop':'articleBody'})#.get_text().strip() if html.find(attrs={'itemprop':'articleBody'}) else ""
            text = text.get_text().strip() if text else ""

            #skip article if less than the minimum words threshold
            if len(text.split()) < app.config['MINIMUM_WORDS_PER_ARTICLE']:
                return {}

            headline = html.find(attrs={'itemprop':'headline'})
            headline = headline.get_text().strip() if headline else ""

            subheadline = html.find(attrs={'class':'subheadline'})
            subheadline = subheadline.get_text().strip() if subheadline else ""

            date = html.find(attrs={'class':'datefrom'})
            date = date.get_text().strip() if date else str(datetime.now().strftime('%d/%m/%Y'))

            author = html.find(attrs={'itemprop':'author'})
            author = author.get_text().strip() if author else '\"Sin firmar\"'

            categories = parsed_url.path.split('/')[1:3]

            labels = [topic.find('a').get_text().strip() 
                    if topic.find('a') else "" 
                    for topic in html.find_all(attrs={'class':'topic'})]

        except Exception as e:
            print(e, parsed_url.path[1:])
            return {}
    
    if parsed_url.netloc == 'www.laprovincia.es' or parsed_url.netloc == 'www.eldia.es':
        try:
            text = html.find(attrs={'itemprop':'articleBody'})
            text = text.get_text().strip() if text else ""

            #skip article if less than the minimum words threshold
            if len(text.split()) < app.config['MINIMUM_WORDS_PER_ARTICLE']:
                return {}

            headline = html.find(attrs={'itemprop':'headline'})
            headline = headline.get_text().strip() if headline else ""

            subheadline = html.find(attrs={'itemprop':'description'})
            subheadline = subheadline.get_text().strip() if subheadline else ""

            date = html.find(attrs={'itemprop':'dateCreated'})
            date = date.get_text().split('|')[0].strip() if date else str(datetime.now().strftime('%d/%m/%Y'))
            
            author = html.find(attrs={'itemprop':'author'})
            author = author.get_text().title().strip() if author else '\"Sin firmar\"'

            categories = parsed_url.path.split('/')[1:3]

            labels = [x.get_text() 
                        for x in html.find(attrs={'id':'listaTags'}).findChildren('a')[1:]]\
                        if html.find(attrs={'id':'listaTags'}) else []

        except Exception as e:
            print(e, parsed_url.path[1:])
            return {}

    if parsed_url.netloc == 'www.canarias24horas.com':
        try:

            text = html.find(attrs={'class':'itemFullText'})
            text = text.get_text().strip() if text else ""

            #skip article if less than the minimum words threshold
            if len(text.split()) < app.config['MINIMUM_WORDS_PER_ARTICLE']:
                return {}

            headline = html.find(attrs={'class':'itemTitle'})
            headline = headline.get_text().strip() if headline else ""

            subheadline = html.find(attrs={'class':'itemIntroText'})
            subheadline = subheadline.get_text().strip() if subheadline else ""

            date = html.find(attrs={'class':'gkDate'})
            date = date.get_text().strip() if date else str(datetime.now().strftime('%d/%m/%Y'))
            
            author = html.find(attrs={'class':'itemAuthor'})
            author = author.get_text().title().strip().split()[-1] if author else '\"Sin firmar\"'

            categories = parsed_url.path.split('/')[1:3]

            labels = [topic.get_text() 
                    for topic in html.find(attrs={'class':'itemTags'}).findChildren('a')]\
                    if html.find(attrs={'class':'itemTags'}) else []

        except Exception as e:
            print(e, parsed_url.path[1:])
            return {}

    if parsed_url.netloc == 'canariasnoticias.es':
        try:
            
            text = ' '.join([x.get_text().strip() for x in html.find(attrs={'class':'noticia-body'}).findChildren('p')]) \
                    if html.find(attrs={'class':'noticia-body'}) else ""

            #skip article if less than the minimum words threshold
            if len(text.split()) < app.config['MINIMUM_WORDS_PER_ARTICLE']:
                return {}

            headline = html.find('h1', attrs={'class':'title'})
            headline = headline.get_text().strip() if headline else ""

            subheadline = html.find('h3', attrs={'class':'subtitle'})
            subheadline = subheadline.get_text().strip() if subheadline else ""

            date = html.find(attrs={'class':'date'})
            date = date.get_text().strip() if date else str(datetime.now().strftime('%d/%m/%Y'))
            
            author = html.find(attrs={'class':'author'})
            author = author.get_text().title().strip() if author else '\"Sin firmar\"'

            categories = parsed_url.path.split('/')[1:3]

            labels = []
         
        except Exception as e:
            print(e, parsed_url.path[1:])
            return {}
        
    if parsed_url.netloc == 'tribunadecanarias.es':
        try:

            text = ' '.join([x.get_text().strip() for x in html.find(attrs={'itemprop':'articleBody'}).findChildren('p')])\
                if html.find(attrs={'itemprop':'articleBody'}) else ""

            #skip article if less than the minimum words threshold
            if len(text.split()) < app.config['MINIMUM_WORDS_PER_ARTICLE']:
                return {}

            headline = html.find(attrs={'itemprop':'headline'})
            headline = headline.get_text().strip() if headline else ""

            subheadline = html.find(attrs={'class':'subheadline'})
            subheadline = subheadline.get_text().strip() if subheadline else ""

            date = html.find(attrs={'id':'t1'})
            date = date.get_text().strip() if date else str(datetime.now().strftime('%d/%m/%Y'))

            author = html.find(attrs={'itemprop':'author'})
            author = author.get_text().title().strip() if author else '\"Sin firmar\"'

            categories = parsed_url.path.split('/')[1:3]

            labels = []

        except Exception as e:
            print(e, parsed_url.path[1:])
            return {}


    #save categories in one
    #extracted data in dict form
    data_dict = {   
                    'newspaper':parsed_url.netloc,
                    'news_link':parsed_url.path[1:],
                    'headline':headline,
                    'subhead':subheadline,
                    'author':author,
                    'date':date,
                    'raw_text':text,
                    'categories':categories,
                    'labels':labels,
                    'term_freq':[],
                    'scrape_date':datetime.now(),

                }
    
    return data_dict

def calculate_tf(doc):
    """Given text document, return dict of {stemmed_word:term_freq} 
    word_frequency_in_doc/total#ofwords
    """
    
    #separate stemming from cleaning to make it easier to control raw and stem words
    
    #clean words
    word_list = clean(doc) 

    #document length
    doc_len = len(word_list)

    #stemm and remove stopwords
    stemmer = SnowballStemmer("spanish")
    stem_list = [stemmer.stem(word) for word in word_list 
                        if word not in stopwords.words('spanish')]
   
    #calculate frequency of every word in list
    freq_dict = collections.Counter([word for word in stem_list]) # dict of word:frequency
    
    # normalise tf by diving its frequency/doc_len
    tf_dict = { key:val/doc_len for key,val in freq_dict.items()}
   
    return tf_dict

def clean(doc):
    """Given string of text, return a list of 
    lowercase, no punctuation words - """

    #separate stemming from clean func to make it easier to handle raw/Stem versions

    #lowercase
    doc = doc.lower()

    #remove punctuation + white space
    doc = doc.translate(str.maketrans('', '', string.punctuation)).strip()

    #tokenization
    WORD = re.compile(r'\w+')
    words = WORD.findall(doc)

    words = [w for w in words if len(w) < app.config['MAXIMUM_WORD_LENGTH']]

    return words

def calculate_word_idf(total_n_documents, articles_with_word):
    """Given a word and the repo of documents and words
    calculate the word's IDF - log(total#ofdocs/#ofdocswithWord) """ 
  
    #dict comprenhension to calculate each word idf {word['idf']:inverse_doc_freq}
    try:
        return float(math.log(total_n_documents/articles_with_word))
    except Exception as e:
        print(e)
    #save data in word repo

def build_tfidf_dict(term_freq,Words_Repo):
    """ returns a dict {word-n:tfidf-score} given an 
    tf dictionary {word:tf-score} and a word repository"""

    tfidf_dict = {}

    for word, term_freq in term_freq.items():

            #get idf of the current word we are iterating
            w_idf = Words_Repo.query.filter(Words_Repo.word_stemm == word).first().idf
        
            #fail check as both idf and tf have to be positive
            if w_idf < 0 or term_freq < 0:
                print('(INVALID) Negative IDF or TF', word)
                
            #store new tfidf score in local dict
            tfidf_dict[word] = term_freq * w_idf
    
    return tfidf_dict

def rank_sentences(doc,tfidf_dict,include_words=False):
    """given text document and the document tfidf_dict {word:word_tfidfscore}, 
    return list of ranked senteces and its score [(sent,score),(sen2,score2)]"""
    
    ranked_sentences = []
    sentences = doc_to_sentence(doc)
    
    for sentence in sentences:
        
        #stemm and remove stopwords
        stemmer = SnowballStemmer("spanish")
        word_list = [stemmer.stem(word) for word in clean(sentence) 
                            if word not in stopwords.words('spanish')]

        score = sum([tfidf_dict[word] for word in word_list])
        ranked_sentences.append((sentence,score))

    return ranked_sentences

def doc_to_sentence(doc):
    """ given a doc, return a list of its sentences"""
    return [s.strip() for s in doc.split('. ')]

def get_top_words(doc,tfidf_dict,n_words=app.config['TOP_WORDS_NUMBER']):
    """Given text doc, and its tfidf dict {word:tfidf_score} return list of top X words"""

    stemmer = SnowballStemmer("spanish")
    word_list = [stemmer.stem(word) for word in clean(doc) 
                    if word not in stopwords.words('spanish')]
    words_score = [(x,tfidf_dict[x]) for x in set([word for word in word_list])] #set to avoid including same words twice
    top_words = sorted(words_score,key=lambda kv: kv[1],reverse=True)[0:n_words]

    # return raw words in order
    #result = [word[1] for top in top_words for word in set(word_list) if top[0] in word]

    return top_words

def summarizer(ranked_sentences,reduce_by=0.5):
    """given a doc's ranked sentences, give summary of top X sentences"""
    
    n_of_sentences = math.ceil(len(ranked_sentences)*(1-reduce_by))
    summary_list = []
    
    top = sorted(ranked_sentences,key=lambda kv: kv[1],reverse=True)[:n_of_sentences]
        
    for sentence in ranked_sentences:
        if sentence in top:
            summary_list.append(sentence[0])
 
    summary = ". ".join(x for x in summary_list)
    return summary 

