"""

Copyright 2019, Pablo Sanderson Ramos

nlp_scorer contains the main functions to calculate articles tf, 
"""
"""
todo:   summary sometimes return empty string
        create doc_repo structure {'headline':1,'link':1, 'cat':['1','2']}
        create word_repo structure{'word':{'doc_freq':0,'idf':0}}
        persist data (database,file?)
        ngrams (2-size,3-size)
"""
import helpers #get all the helper functions
import collections #for fast frequency counters
import math #calculate tfidf-log


def calculate_tf(doc):
    """Given text document, return dict of {stemmed_word:term_freq}. 
    word_frequency_in_doc/total#ofwords
    """
    
    #before using, check if tf is not already calculated for text
    
    word_list = helpers.clean(doc) # retrieves list of processed(clean) words of doc
    doc_len = len(word_list) # how many words in doc
   
    freq_dict = collections.Counter(word_list) # dict of word:frequency
    
    # normalise tf by diving its frequency/doc_len
    tf_dict = { key:val/doc_len for key,val in freq_dict.items()}
    
    #update word_repo word frequency to calculate IDF log(totaldocuments/documentsWithWord)
    #[update_word_repo(word,WORD_REPO) for word in set(word_list)] #set so we dont count wordsx2 in a doc
   
    return tf_dict

def calculate_word_idf(word, docs_repo,words_repo):
    """Given a word and the repo of documents and words
    calculate the word's IDF - log(total#ofdocs/#ofdocswithWord) """ 
  
    docs_len = len(docs_repo)
    word = helpers.clean(word)
    
    #dict comprenhension to calculate each word idf {word['idf']:inverse_doc_freq}
    try:
        return math.log(docs_len/words_repo[word]['freq'])
    except Exception as e:
        print(e)
    #save data in word repo

def calculate_mass_idf(docs_repo, words_repo):
    """ given a document repo and a word repo, update words_repo idf
    for every word - log(total#ofdocs/#ofdocswithWord) """

    docs_len = len(docs_repo)
    try:
        for key,val in words_repo.items():
            val['idf'] = math.log(docs_len/val['freq'])

    except Exception as e:
        print(e)

def calculate_tfidf(word_tf, word_idf):
    """given a word term_freq and its idf, return its tfidf"""
    
    return word_tf*word_idf

def sentences(doc):
    """ given a doc, return a list of its sentences"""
    return [s.strip() for s in doc.split('. ')]

def rank_sentences(doc,tfidf_dict,include_words=False):
    """given document and the document tfidf_dict {word:word_tfidfscore}, return list of
    ranked senteces and its score [(sent,score),(sen2,score2)]"""
    
    ranked_sentences = []
    
    for sentence in sentences(doc):
        
        word_list = helpers.clean(sentence)
        if len(word_list) < 5:
            continue #if less than 5 words in sentence, skip  
        score = sum([tfidf_dict[word] for word in word_list])
    
        ranked_sentences.append((sentence,score))
    
    if include_words:
        pass #include calculate top words (of doc, of included sentences?)
    
    return ranked_sentences

def top_words(word_list,tfidf_dict,n_words=5):
    """Given list of words, and its tfidf dict {word:tfidf_score} return list of top X words"""

    words_score = [(word,tfidf_dict[word]) for word in set(word_list)] #set to avoid including same words twice
    top_words = sorted(words_score,key=lambda kv: kv[1],reverse=True)[0:n_words]

    return top_words

def summarizer(doc,tfidf_dict,reduce_by=0.5):
    """given document and its tfidf_dictionary, give summary of top X sentences"""
    
    ranked_sentences  = rank_sentences(doc,tfidf_dict)
    
    n_of_sentences = round(len(ranked_sentences)*(1-reduce_by))
    summary_list = []
    
    top = sorted(ranked_sentences,key=lambda kv: kv[1],reverse=True)[:n_of_sentences]
        
    for sentence in ranked_sentences:
        if sentence in top:
            summary_list.append(sentence[0])
 
    summary = ". ".join(x for x in summary_list)
    return summary 



if __name__ == "__main__":
    print('hola')
    print(summarizer('Hola hola hoy hace frio. Frio mesa frio que hola hoy. Hoy hace Hola frio hoy hoy',{'hol':0.1,'hoy':0.2,'ho':0.2,'hace':0.3,'hac':0.3,'frio':0.4,'fri':0.4,'mesa':0.5,'mes':0.5},0.9))