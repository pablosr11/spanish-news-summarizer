"""

Copyright 2019, Pablo Sanderson Ramos

nlp_scorer contains the main functions to calculate articles tf, 
"""
"""
todo:   summary sometimes return empty string
        ngrams (2-size,3-size)
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
        score = sum([tfidf_dict[word[0]] for word in word_list])
    
        ranked_sentences.append((sentence,score))
    
    
    return ranked_sentences

def top_words(doc,tfidf_dict,n_words=5):
    """Given list of words, and its tfidf dict {word:tfidf_score} return list of top X words"""

    word_list = helpers.clean(doc)
    words_score = [(x,tfidf_dict[x]) for x in set([word[0] for word in word_list])] #set to avoid including same words twice
    top_words = sorted(words_score,key=lambda kv: kv[1],reverse=True)[0:n_words]

    return top_words

def summarizer(doc,tfidf_dict,reduce_by=0.5):
    """given document and its tfidf_dictionary, give summary of top X sentences"""
    
    ranked_sentences  = rank_sentences(doc,tfidf_dict)
    
    n_of_sentences = math.ceil(len(ranked_sentences)*(1-reduce_by))
    summary_list = []
    
    top = sorted(ranked_sentences,key=lambda kv: kv[1],reverse=True)[:n_of_sentences]
        
    for sentence in ranked_sentences:
        if sentence in top:
            summary_list.append(sentence[0])
 
    summary = ". ".join(x for x in summary_list)
    return summary 



if __name__ == "__main__":

    print(summarizer('La titular del juzgado de violencia contra la mujer de Arona (Tenerife) procedera este lunes a grabar el testimonio del niño de 6 años que sobrevivio la semana pasada al asesinato de su madre y su hermano, presuntamente a manos de su padre en una cueva del sur de la isla, para evitar que tenga que volver a declarar en sede judicial. Esta diligencia, denominada "prueba preconstituida", se lleva a cabo fuera del juzgado de Arona y el testimonio es grabado para evitar que el niño tenga que volver a declarar en sede judicial y con ello minimizar los "efectos de victimacion", segun fuentes juridicas. En el interrogatorio estaran presentes, ademas de la jueza, la representacion del Ministerio Fiscal, la defensa del acusado y un equipo tecnico especializado en tratar con menores en este tipo de situaciones. El niño, de nacionalidad alemana al igual que su familia, fue encontrado el martes de la semana pasada por unos vecinos cuando huia de la cueva en la que supuestamente su padre ataco con piedras a su madre y a su hermano de 10 años. El testimonio del niño llevo a la detencion de su padre y, tras un dispositivo de busqueda, el miercoles fueron hallados los cadaveres con signos de violencia. El Gobierno de Canarias sigue manteniendo la tutela del niño, ya que ningun familiar se ha desplazado de momento a la isla desde Alemania, aunque un sacerdote visita con autorizacion judicial y de la familia al menor. Se espera que proximamente haya alguna resolucion judicial acerca de la tutela del pequeño.',{'titul': 0.012476262887086049, 'juzg': 0.04063626083895473, 'violenci': 0.03717667089609877, 'muj': 0.015980023536257035, 'aron': 0.04063626083895473, 'tenerif': 0.012476262887086049, 'proced': 0.018588335448049383, 'lun': 0.020318130419477366, 'grab': 0.03717667089609877, 'testimoni': 0.0609543912584321, 'niñ': 0.07990011768128519, '6': 0.020318130419477366, 'años': 0.008396857091980533, 'sobreviv': 0.025691364377306403, 'seman': 0.0264302029804407, 'pas': 0.0068501201903727015, 'asesinat': 0.01717499004654586, 'madr': 0.0264302029804407, 'herman': 0.03434998009309172, 'presunt': 0.01717499004654586, 'man': 0.012476262887086049, 'padr': 0.04794007060877111, 'cuev': 0.04063626083895473, 'sur': 0.020318130419477366, 'isla': 0.01820340839032953, 'evit': 0.03717667089609877, 'volv': 0.02236253996544084, 'declar': 0.024952525774172098, 'sed': 0.03196004707251407, 'judicial': 0.06869996018618343, 'diligent': 0.02254822400437489, 'denomin': 0.02254822400437489, 'prueb': 0.01403184967361435, 'preconstitu': 0.025691364377306403, 'llev': 0.01731723143157064, 'cab': 0.012476262887086049, 'ello': 0.01321510149022035, 'minimiz': 0.031064598335135436, 'efect': 0.018588335448049383, 'victim': 0.031064598335135436, 'segun': 0.008239489969504112, 'fuent': 0.014944896461648333, 'jurid': 0.025691364377306403, 'interrogatori': 0.031064598335135436, 'present': 0.00865861571578532, 'ademas': 0.005808036024891387, 'juez': 0.020318130419477366, 'represent': 0.01321510149022035, 'ministeri': 0.025691364377306403, 'fiscal': 0.020318130419477366, 'defens': 0.018588335448049383, 'acus': 0.018588335448049383, 'equip': 0.010606789578428002, 'tecnic': 0.014944896461648333, 'especializ': 0.031064598335135436, 'trat': 0.01403184967361435, 'menor': 0.0264302029804407, 'tip': 0.01717499004654586, 'situacion': 0.01321510149022035, 'nacional': 0.0067584416225063655, 'aleman': 0.018588335448049383, 'igual': 0.015980023536257035, 'famili': 0.03742878866125814, 'encontr': 0.018588335448049383, 'mart': 0.015980023536257035, 'vecin': 0.01717499004654586, 'hui': 0.031064598335135436, 'supuest': 0.02254822400437489, 'atac': 0.025691364377306403, 'piedr': 0.015980023536257035, '10': 0.01321510149022035, 'detencion': 0.020318130419477366, 'tras': 0.007103028929257016, 'disposit': 0.031064598335135436, 'busqued': 0.025691364377306403, 'miercol': 0.01717499004654586, 'hall': 0.01717499004654586, 'cadaver': 0.031064598335135436, 'sign': 0.031064598335135436, 'gobiern': 0.008239489969504112, 'canari': 0.0030059343489051427, 'sig': 0.010211639454518908, 'manten': 0.020318130419477366, 'tutel': 0.04063626083895473, 'ningun': 0.012476262887086049, 'desplaz': 0.02254822400437489, 'moment': 0.007463649205496496, 'alemani': 0.01717499004654586, 'aunqu': 0.007103028929257016, 'sacerdot': 0.018588335448049383, 'visit': 0.01321510149022035, 'autoriz': 0.01717499004654586, 'esper': 0.010606789578428002, 'proxim': 0.01118126998272042, 'algun': 0.011801756088716826, 'resolu': 0.025691364377306403, 'acerc': 0.02254822400437489, 'pequeñ': 0.014944896461648333},\
        0.5))
    print('-----nlp_scorer.py')