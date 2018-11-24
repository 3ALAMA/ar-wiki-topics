import os 
import json 
from collections import defaultdict
from gensim import corpora, models

def load_json_corpus(corpus_dir):
    corpus = list()
    for subdir, dirs, files in os.walk(corpus_dir):
        for f in files:
            wiki_file = os.path.join(subdir, f)
            #print('reading', wiki_file)
            with open(wiki_file, encoding='utf-8') as wiki_reader:
                lines = wiki_reader.readlines()
                for line in lines:
                    json_doc = json.loads(line)
                    doc_id = json_doc['id']
                    title = json_doc['title']
                    text = json_doc['text']
                    corpus.append((doc_id, title, text))
    return corpus
    
    
def build_model(corpus_path, min_freq, topics):
    print('min freq:', min_freq, 'topics:', topics)
    wiki_corpus = load_json_corpus(corpus_path)
    print('corpus loaded')
    texts = [[word for word in d.split()] for i, t, d  in wiki_corpus]
    print('texts collected')
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    
    texts = [[token for token in text if frequency[token] > min_freq] for text in texts]
    print('texts filtered')
    dictionary = corpora.Dictionary(texts)
    dictionary.save('ar_wiki_20181020_{}freq_{}topics.dict'.format(min_freq, topics))
    print('dictionary saved')
    corpus = [dictionary.doc2bow(text) for text in texts]
    print('gensim corpus transformed')
    tfidf = models.TfidfModel(corpus) 
    print('tfidf modeled')
    corpus_tfidf = tfidf[corpus]
    print('tfidf corpus transformed')
    # initialize an LSI transformation
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=topics) 
    print('lsi corpus built')
    # create a double wrapper over the original corpus: 
    # bow->tfidf->fold-in-lsi
    corpus_lsi = lsi[corpus_tfidf] 
    print('lsi corpus transformed')
    lsi.save('ar_wiki_20181020_{}freq_{}topics.lsi'.format(min_freq, topics)) 
    print('lsi corpus saved')
    print('done!')



corpus_path = '../arwikiExtracts/20181020/' 
# build_model(corpus_path, min_freq=3, topics=500)
# build_model(corpus_path, min_freq=5, topics=300)
build_model(corpus_path, min_freq=7, topics=300)
