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

    # it doesnt get content that loads with JS - solution would query directly those urls
    # https://gohighbrow.com/scraping-javascript-heavy-websites/ not implemented

    parsed_url = urlparse(url)
    html = helpers.get_html(url) #get bs4 object

    links = [] #store news links

    # give parameters to scrape website depending on link
    if parsed_url.netloc == 'www.canarias7.es':
        for link in html.find_all(['h2','h3','div'], attrs={'class':'headline'}): #include div (more news but more noise)
            if link.parent.has_attr('href'):# skip None links - without the structure (normally voting polls etc)
                links.append(link.parent['href'])
            

    if parsed_url.netloc == 'www.laprovincia.es':
        for link in html.find_all('a', attrs={'data-tipo':'noticia'}):
            links.append(link['href'])

    if parsed_url.netloc == 'www.eldia.es':
        for link in html.find_all('a', attrs={'data-tipo':'noticia'}):
            links.append(link['href'])
    
    if parsed_url.netloc == 'www.noticanarias.com':
        for link in html.find_all('a', attrs={'itemprop':'url'}):
            links.append(link['href'])

    if parsed_url.netloc == 'www.canarias24horas.com':
        for link in html.find_all('h4', attrs={'class':'nspHeader'}):
            links.append(link.findChildren('a')[0]['href'])
    
    
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
            author = html.find(attrs={'itemprop':'author'}).get_text().strip().title()\
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
            author = html.find(attrs={'itemprop':'author'}).get_text().strip().title()\
                if html.find(attrs={'itemprop':'author'}) else 'Anónimo'
            n_comments = html.find(attrs={'class':'textveces'}).get_text().strip()\
                if html.find(attrs={'class':'textveces'}) else 0
            categories = parsed_url.path.split('/')[1:3]
            labels = [x.get_text() for x in html.find(attrs={'id':'listaTags'}).findChildren('a')[1:]]\
                if html.find(attrs={'id':'listaTags'}) else []
        except Exception as e:
            print(e, parsed_url.path[1:])

    if parsed_url.netloc == 'www.eldia.es':
        try:
            text = html.find(attrs={'itemprop':'articleBody'}).get_text().strip()\
                if html.find(attrs={'itemprop':'articleBody'}) else ""
            headline = html.find(attrs={'itemprop':'headline'}).get_text().strip()\
                if html.find(attrs={'itemprop':'headline'}) else ""
            subheadline = html.find(attrs={'itemprop':'description'}).get_text().strip()\
                if html.find(attrs={'itemprop':'description'}) else ""
            date = html.find(attrs={'itemprop':'dateCreated'}).get_text().split('|')[0].strip()\
                if html.find(attrs={'itemprop':'dateCreated'}) else ""
            author = html.find(attrs={'itemprop':'author'}).get_text().strip().title()\
                if html.find(attrs={'itemprop':'author'}) else 'Anónimo'
            n_comments = html.find(attrs={'class':'textveces'}).get_text().strip()\
                if html.find(attrs={'class':'textveces'}) else 0
            categories = parsed_url.path.split('/')[1:3]
            labels = [x.get_text() for x in html.find(attrs={'id':'listaTags'}).findChildren('a')[1:]]\
                if html.find(attrs={'id':'listaTags'}) else []
        except Exception as e:
            print(e, parsed_url.path[1:])

    if parsed_url.netloc == 'www.noticanarias.com':
        try:
            text = ' '.join([x.get_text().strip() for x in html.find(attrs={'itemprop':'articleBody'}).findChildren('p')])\
                if html.find(attrs={'itemprop':'articleBody'}) else ""
            headline = html.find(attrs={'itemprop':'headline'}).get_text().strip()\
                if html.find(attrs={'itemprop':'headline'}) else ""
            subheadline = ""
            date = html.find(attrs={'class':'vw-post-date updated'}).findChildren('time')[0]['datetime'].split('T')[0].strip()\
                if html.find(attrs={'class':'vw-post-date updated'}) else ""
            author = html.find(attrs={'itemprop':'name'}).get_text().strip().title()\
                if html.find(attrs={'itemprop':'name'}) else 'Anónimo'
            n_comments = ""
            categories = ['','']
            labels = [x.get_text() for x in html.find_all('a',attrs={'rel':'tag'})]\
                if html.find_all('a',attrs={'rel':'tag'}) else []
        except Exception as e:
            print(e, parsed_url.path[1:])

    if parsed_url.netloc == 'www.canarias24horas.com':
        try:
            text = html.find(attrs={'class':'itemFullText'}).get_text().strip()\
                if html.find(attrs={'class':'itemFullText'}) else ""
            headline = html.find(attrs={'class':'itemTitle'}).get_text().strip()\
                if html.find(attrs={'class':'itemTitle'}) else ""
            subheadline = html.find(attrs={'class':'itemIntroText'}).get_text().strip()\
                if html.find(attrs={'class':'itemIntroText'}) else ""
            date = html.find(attrs={'class':'gkDate'}).get_text().strip()\
                if html.find(attrs={'class':'gkDate'}) else ""
            author = html.find(attrs={'class':'itemAuthor'}).get_text().strip().title().split()[-1]\
                if html.find(attrs={'class':'itemAuthor'}) else 'Anónimo'
            n_comments = ""
            categories = parsed_url.path.split('/')[1:3]
            labels = [topic.get_text() for topic in html.find(attrs={'class':'itemTags'}).findChildren('a')]\
                if html.find(attrs={'class':'itemTags'}) else []
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
    pass
    #print(get_links('http://www.eldigitaldecanarias.net/'))
    #for x in get_links('http://www.eldigitaldecanarias.net'):
    #    print(extract_data(x))