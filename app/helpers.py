"""
Copyright 2019, Pablo Sanderson Ramos

Group of general helper functions
"""

"""
todo: ngrams
"""
import requests #download websites
from bs4 import BeautifulSoup #scrape websites
import lxml
import string #remove punctuation with string.translate

from nltk.stem.snowball import SnowballStemmer #ciudades -> ciudad

from nltk.corpus import stopwords #for spanish stopwords



def get_html(url):
    """Given URL, output BeautifulSoup object of html content"""

    raw_data = requests.get(url)
    html = BeautifulSoup(raw_data.content, 'lxml')

    return html

def clean(doc):
    """Given string of text, return a list of tuples with
    (raw_word,stem_word) of its words clean of punctuation, stopwords etc"""

    #separate stemming from clean func to make it easier to handle raw/Stem versions

    doc = doc.lower()
    
    #remove string punctuation
    doc = doc.translate(str.maketrans('', '', string.punctuation))

    stemmer = SnowballStemmer("spanish")

    # if single word, stemm it and return it
    if len(doc.split()) == 1:
        return stemmer.stem(doc),doc if doc not in stopwords.words('spanish') else ""

    #stemm and remove stopwords
    cleaned = [(stemmer.stem(word),word) for word in doc.split()\
               if word not in stopwords.words('spanish')\
               if len(word)<25] #skip words longer than 25 to avoid html
    
    return cleaned

def sentences(doc):
    """ given a doc, return a list of its sentences"""
    return [s.strip() for s in doc.split('. ')]




if __name__ == "__main__":
    print(clean('HOla'))