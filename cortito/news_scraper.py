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
        # try to find all <a> with title tag
        for link in html.find_all(['h2','h3','div'], attrs={'class':'headline'}, limit=n_links): #include div (more news but more noise)
            if not link.parent.has_attr('href'):# skip None links - without the structure (normally voting polls etc)
                continue
            links.append(link.parent['href'])
    if parsed_url.netloc == 'www.laprovincia.es':
        for link in html.find_all('a', attrs={'data-tipo':'noticia'}):
            links.append(link['href'])
    
    return links

def extract_data(url):
    """Given news article URL, return a dict with its data organised"""

    #author link?

    parsed_url = urlparse(url)
    html = helpers.get_html(url)

    if parsed_url.netloc == 'www.canarias7.es':
        try:
            text = html.find(attrs={'itemprop':'articleBody'}).get_text().strip()\
                if html.find(attrs={'itemprop':'articleBody'}) else ""
            headline = html.find(attrs={'itemprop':'headline'}).get_text().strip()\
                if html.find(attrs={'itemprop':'headline'}) else ""
            subheadline = html.find(attrs={'class':'subheadline'}).get_text().strip()\
                if html.find(attrs={'class':'subheadline'}) else ""
            date = html.find(attrs={'class':'datefrom'}).get_text().strip()\
                if html.find(attrs={'class':'datefrom'}) else ""
            author = html.find(attrs={'itemprop':'author'}).get_text().strip()\
                if html.find(attrs={'itemprop':'author'}) else 'Anónimo'
            n_comments = html.find(attrs={'class':'numComments'}).get_text().strip()\
                if html.find(attrs={'class':'numComments'}) else 0
            categories = parsed_url.path.split('/')[1:3]
            labels = [topic.find('a').get_text() for topic in html.find_all(attrs={'class':'topic'})]
        except Exception as e:
            print(e, parsed_url.path[1:])

    if parsed_url.netloc == 'www.laprovincia.es':
        try:
            text = html.find(attrs={'itemprop':'articleBody'}).get_text().strip()\
                if html.find(attrs={'itemprop':'articleBody'}) else ""
            headline = html.find(attrs={'itemprop':'headline'}).get_text().strip()\
                if html.find(attrs={'itemprop':'headline'}) else ""
            subheadline = html.find(attrs={'itemprop':'description'}).get_text().strip()\
                if html.find(attrs={'itemprop':'description'}) else ""
            date = html.find(attrs={'itemprop':'dateCreated'}).get_text().split('|')[0].strip()\
                if html.find(attrs={'itemprop':'dateCreated'}) else ""
            author = html.find(attrs={'itemprop':'author'}).get_text().strip()\
                if html.find(attrs={'itemprop':'author'}) else 'Anónimo'
            n_comments = html.find(attrs={'class':'textveces'}).get_text().strip()\
                if html.find(attrs={'class':'textveces'}) else 0
            categories = parsed_url.path.split('/')[1:3]
            labels = [] #[topic.get_text() for topic in html.find(attrs={'id':'listaTags'}).findChildren('a')]
        except Exception as e:
            print(e, parsed_url.path[1:])
    
    
   #save categories in one
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
    a= extract_data('https://www.laprovincia.es/gran-canaria/2019/05/06/cabildo-esconde-juez-documentos-adquisicion/1172010.html')
    print(a)
    pass