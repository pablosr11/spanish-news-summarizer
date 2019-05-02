"""

Copyright 2019, Pablo Sanderson Ramos

news_scraper holds the two main functions to gather links and data from news articles URL
"""
"""
todo:   fail-checks on .finds
        extremely slow
"""

from urllib.parse import urlparse #parse the url
import helpers #get all the helper functions

def get_links(url,n_links=5):
    """Given a news outlet main website, return its news links. Identifies where links are depending on outlet"""

    parsed_url = urlparse(url)
    html = helpers.get_html(url) #get bs4 object

    links = [] #store news links

    # give parameters to scrape website depending on link
    if parsed_url.netloc == 'www.canarias7.es':
        for link in html.find_all(['h2','h3','div'], attrs={'class':'headline'}, limit=n_links): #include div (more news but more noise)
            if not link.parent.has_attr('href'):
                #print('NO LINK, ',link.get_text().strip())
                continue    # skip None links - without the structure (normally voting polls etc)
            links.append(link.parent['href'])

    return links

def extract_data(url):
    """Given news article URL, return a dict with its data organised"""

    parsed_url = urlparse(url)
    html = helpers.get_html(url)

    if parsed_url.netloc == 'www.canarias7.es':
        #if 'multimedia/videos/' in parsed_url.path:
        #    return 'Article is a video', parsed_url.path[1:]
        try:
            text = html.find(attrs={'itemprop':'articleBody'}).get_text().strip()\
                if html.find(attrs={'itemprop':'articleBody'}) else ""
            headline = html.find(attrs={'itemprop':'headline'})#.get_text().strip() if html.find(attrs={'itemprop':'headline'}) is not None else ""
            subheadline = html.find(attrs={'class':'subheadline'})
            date = html.find(attrs={'class':'datefrom'})
            author = html.find(attrs={'itemprop':'author'})
            n_comments = html.find(attrs={'class':'numComments'}) #dont collect as it keeps changing and we only scrape once.
            categories = parsed_url.path.split('/')[1:3]
            labels = [topic.find('a').get_text() for topic in html.find_all(attrs={'class':'topic'})]
        except Exception as e:
            print(e, parsed_url.path[1:])

    #get_text and strip() all elements of list that require it
    to_text = [headline,subheadline,date,author,n_comments] 
    [headline,subheadline,date,author,n_comments] =\
        [x.get_text().strip() if x else "" for x in to_text]
   
   # extracted data in dict form
    data_dict = {   
                    'newspaper':parsed_url.netloc,
                    'news_link':parsed_url.path[1:],
                    'headline':headline,
                    'subhead':subheadline,
                    'author':author,
                    'date':date,
                    'raw_text':text,
                    'n_comments':n_comments,
                    'main_cat':categories[1],
                    'sub_cat':categories[0],
                    'labels':labels
                }
    
    return data_dict



if __name__ == "__main__":
    pass