"""

Copyright 2019, Pablo Sanderson Ramos

news_scraper holds the two main functions to gather links and data from news articles URL
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_links(url,n_links=5):

    parsed_url = urlparse(url)
    html = get_html(url) #get bs4 object

    # give parameters to scrape website depending on link
    if parsed_url.netloc == 'www.canarias7.es':
        links = [x.parent['href'] if x.parent.has_attr('href') else "0"\
            for x in html.find_all(['h2','h3','div'],\
                attrs={'class':'headline'},\
                limit=n_links)]
            
    return links

def extract_data(url):
    """Given news article URL, return a dict with its data organised"""

    parsed_url = urlparse(url)
    html = get_html(url)

    if parsed_url.netloc == 'www.canarias7.es':
        text = html.find(attrs={'itemprop':'articleBody'})
        headline = html.find(attrs={'itemprop':'headline'})#.get_text().strip() if html.find(attrs={'itemprop':'headline'}) is not None else ""
        subheadline = html.find(attrs={'class':'subheadline'})
        date = html.find(attrs={'class':'datefrom'})
        author = html.find(attrs={'itemprop':'author'})
        n_comments = html.find(attrs={'class':'numComments'})
        categories = parsed_url.path.split('/')[1:3]
        labels = [topic.find('a').get_text() for topic in html.find_all(attrs={'class':'topic'})]

    #get_text and strip() all elements of list that require it
    to_text = [headline,subheadline,date,author,text,n_comments] 
    [headline,subheadline,date,author,text,n_comments] =\
        [x.get_text().strip() if x else "" for x in to_text]
   
   # extracted data in dict form
    data_dict = {   
                    'newspaper':parsed_url.netloc.split('.')[1],
                    'news_link':parsed_url.path,
                    'headline':headline,
                    'subhead':subheadline,
                    'author':author,
                    'date':date,
                    'raw_text':text,
                    'n_comments':n_comments,
                    'cat':categories,
                    'labels':labels
                }
    
    return data_dict

def get_html(url):
    """Given URL, output BeautifulSoup object of html content"""

    raw_data = requests.get(url)
    html = BeautifulSoup(raw_data.content, 'lxml')

    return html

if __name__ == "__main__":
    pass