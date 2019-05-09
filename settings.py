
"""
 Copyright 2019 Pablo Sanderson Ramos


"""

#newspapers to analyse
OUTLETS = ['https://www.canarias7.es/', 'https://www.laprovincia.es/','https://www.eldia.es/',\
    'http://www.canarias24horas.com/','http://tribunadecanarias.es/',\
    'https://canariasnoticias.es/']
    #'https://www.noticanarias.com/' 
    # requests.exceptions.ConnectionError: ('Connection aborted.', 
    # RemoteDisconnected('Remote end closed connection without response'))

#waiting time between processes
WAITING_TIME = 60*60 #60min

#time news stay on board from scraping time in hours
TIME_ON_BOARD = 18

#how many articles do we show
ARTICLES_TO_SHOW = 30

# minimum words per article
MINIMUM_WORDS_ARTICLE = 100

# how many updated words to update tfidf of file?
UPDATED_WORDS = 20

# how much (%) to summarize article?
SUMMARIZATION_POINTS = 0.95

#how many top words include?
TOP_WORDS_NUMBER = 10