"""

Copyright 2019, Pablo Sanderson Ramos

nlp_scorer contains the main functions to calculate articles tf, 
"""
"""
todo:   summary sometimes return empty string
        ngrams (2-size,3-size)
        skip sentences < 5 words
        calculate tf does multiple things, simplify and separate
"""
import helpers #get all the helper functions
import collections #for fast frequency counters
import math #calculate tfidf-log


def calculate_tf(doc):
    """Given text document, return dict of {stemmed_word:term_freq} and list of tuples
    containing (stem_word, raw_word) for later use (CHANGE THIS)
    word_frequency_in_doc/total#ofwords
    """
    
    #separate stemming from cleaning to make it easier to control raw and stem words
    
    word_list = helpers.clean(doc) # retrieves list of processed(clean) words of doc
    doc_len = len(word_list) # how many words in doc
   
    freq_dict = collections.Counter([word[0] for word in word_list]) # dict of word:frequency
    
    # normalise tf by diving its frequency/doc_len
    tf_dict = { key:val/doc_len for key,val in freq_dict.items()}
    
    #update word_repo word frequency to calculate IDF log(totaldocuments/documentsWithWord)
    #[update_word_repo(word,WORD_REPO) for word in set(word_list)] #set so we dont count wordsx2 in a doc
   
    return tf_dict, word_list

def calculate_word_idf(total_n_documents, articles_with_word):
    """Given a word and the repo of documents and words
    calculate the word's IDF - log(total#ofdocs/#ofdocswithWord) """ 
  
    #dict comprenhension to calculate each word idf {word['idf']:inverse_doc_freq}
    try:
        return math.log(total_n_documents/articles_with_word)
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

def rank_sentences(doc,tfidf_dict,include_words=False):
    """given document and the document tfidf_dict {word:word_tfidfscore}, return list of
    ranked senteces and its score [(sent,score),(sen2,score2)]"""
    
    ranked_sentences = []
    
    for sentence in helpers.sentences(doc):
        
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

    print(calculate_word_idf(52,6))
    print('-----nlp_scorer.py')