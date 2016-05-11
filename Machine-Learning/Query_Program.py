import string
import re
from elasticsearch import elasticsearch
import urllib3
import os
import math
import operator
from collections import Counter
from pprint import pprint
from stemming.porter import stem
import pickle
import collections

def get_relevance_scores():
    file_name = 'qrels.adhoc.51-100.AP89.txt'
    file = open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\"+file_name,"r")
    rel_hash = collections.OrderedDict()
    for line in file:
        fields = line.split()
        query_id = str(fields[0])
        doc_no = str(fields[2])
        relevance = str(fields[3])
        if query_id in rel_hash.keys():
            rel_hash[query_id][doc_no] = relevance
        else:
            rel_hash[query_id] = collections.OrderedDict()
            rel_hash[query_id][doc_no] = relevance
            
    return rel_hash

def build_queries():
    
    file = "query_desc.51-100.short.txt"
    with open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\"+file) as f:
        queries = f.readlines()
    q_dict = dict()
    
    for query in queries:    
        new_query = query.split('.')
        new_query.pop()
        if len(new_query) > 0 and new_query[0] not in q_dict:
            edit_query=new_query[1].split()        
            edit_query = edit_query[3:]
            edit_query = ' '.join(edit_query)
            edit_query = edit_query.replace(',','')
            edit_query = edit_query.replace('"','')
            edit_query = edit_query.replace('-',' ')
            q_dict[new_query[0]] = edit_query
                
    stop_fname = "stoplist.txt"
    stop_file = open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\"+stop_fname,'r')
    stop_words = []

    for line in stop_file:
        line=line[:-1]
        stop_words.append(line)
    fin_query=''
    query_dict=dict()
    for key in q_dict.keys():    
        fin_query=' '.join([stem(word) for word in q_dict[key].split() if word not in stop_words])    
        query_dict[key]=fin_query
    return query_dict

def build_queries1():
    file = "testing_queries.txt"

    with open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\"+file) as f:
        queries = f.readlines()

    query_dict = dict()

    for queryln in queries:
        
        new_query = queryln.split()
        query_dict[new_query[0]]=' '.join(new_query[1:])
    return query_dict

def okapi_TF(tf, dlen, avg_dlen):
    return (tf/(tf+0.5+(1.5*(dlen/avg_dlen))))

def okapi_BM25(tf,dlen,avg_dlen,df,tf_query,corpus):
    k2=400
    k1=1.2
    b=0.75
    log_fn=math.log((corpus+0.5)/(df+0.5))
    mid_fn=(tf+k1*tf)/(tf+k1*((1-b)+(b*dlen/avg_dlen)))
    query_fn=(tf_query+(k2*tf_query))/(tf_query+k2)
    return log_fn*mid_fn*query_fn

def unigram_laplace(tf,dlen):
    #V=178050
    V=59721
    p_laplace=(tf+1)/(dlen+V)
    return (math.log(p_laplace))

def unigram_jel_mer(tf,dlen,delta_tf,delta_dlen):
    l=0.5
    p_jm=(l*(tf/dlen))+((1-l)*delta_tf/delta_dlen)
    return math.log(p_jm)

def get_results(results):
    doc_details = [(doc['_id'], doc['_score'], doc['fields']['docno'])for doc in results['hits']['hits']]
    return doc_details

def get_results1(results):
    doc_details = [(doc['_id'], doc['_explanation']['details'][0]['details'][0]['details'][0]['value'], doc['fields']['docno'])for doc in results['hits']['hits']]
    return doc_details

def get_dlens():
    
    es = elasticsearch.Elasticsearch("localhost:9200", timeout=10000, max_retries=10, revival_delay=0)
    res = es.search(index="ap_dataset_hw5", body={"query": {"match_all": {}}},size=15000)
    doc_ids=[doc['_id'] for doc in res['hits']['hits']]

    corpus =res['hits']['total']
    i=500
    no_txt=0
    no_text_doc=[]
    dlen_hash=dict()
    while i<=corpus:

        if i!=corpus:
            v=es.mtermvectors(index="ap_dataset_hw5", ids=doc_ids[i-500:i], doc_type='document', fields=['text'], field_statistics='false')
        else:
            v=es.mtermvectors(index="ap_dataset_hw5", ids=doc_ids[12000:i], doc_type='document', fields=['text'], field_statistics='false')
        
        for doc in v['docs']:
            if 'text' in doc['term_vectors']:
                terms=doc['term_vectors']['text']['terms']
                dlen=0
                for term in terms:                
                    tf=doc['term_vectors']['text']['terms'][term.lower()]['term_freq']                
                    dlen+= tf
                dlen_hash[doc['_id']]=dlen
                
        if i<12000:
            i+=500
        elif i==corpus:
            i+=100
        else:
            i=corpus
            
    pickle.dump( dlen_hash, open( "C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\Doc_Lengths", "wb" ) )


es = elasticsearch.Elasticsearch("localhost:9200", timeout=10000, max_retries=10, revival_delay=0)

es.put_script(lang='groovy', id='getTF', body={"script": "_index[field][term].tf()"})
res = es.search(index="ap_dataset_hw5", body={"size": 15000,"query": {"match_all": {}}})

corpus =res['hits']['total']
docs=[doc['_id'] for doc in res['hits']['hits']]
#print(corpus)
print(len(docs))
'''
## Finding Total corpus length

i=500
no_txt=0
no_text_doc=[]
total_dlen=0
while i<=corpus:
    print(i)
    if i!=corpus:
        v=es.mtermvectors(index="ap_dataset_hw5", ids=docs[i-499:i], doc_type='document', fields=['text','docno'], field_statistics='false')
    else:
        v=es.mtermvectors(index="ap_dataset_hw5", ids=docs[12001:i], doc_type='document', fields=['text','docno'], field_statistics='false')
    
    total_dlen_i=0
    for doc in v['docs']:
        if 'text' in doc['term_vectors']:
            terms=doc['term_vectors']['text']['terms']
            total_words_doc=0
            for term in terms:                
                tf=doc['term_vectors']['text']['terms'][term.lower()]['term_freq']                
                total_words_doc+= tf        
          
        total_dlen_i+=total_words_doc
    total_dlen+=total_dlen_i    
    if i<12000:
        i+=500
    elif i==corpus:
        i+=100
    else:
        i=corpus        

print(total_dlen)   #value is 3797502
'''
total_dlen=3797502
avg_dlen=total_dlen/corpus
# Calculating document lengths of individual documents
#get_dlens()
dlen_hash=pickle.load( open( "C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\Doc_Lengths", "rb" ) )
relevance_hash = get_relevance_scores()
query_dict=build_queries1()
#query_dict={'91': 'U.S Army specifi advanc weapon system'}
for query_id,query in query_dict.items():
    output = ''
    okapi_score = dict()
    tf_idf_score = dict()
    bm25_score = dict()
    unigram_laplace_score = dict()
    unigram_jel_mer_score = dict()
    term_counts = Counter(query.split())
    for term in query.split():
        print (term)
        term_org=term
        if term== 'U.S':
            term='u.'        
        doc_hash=dict()
        tf_query=term_counts[term]        
        results = es.search(index='ap_dataset_hw5',body={"query": {"function_score": {"query": {"match": {"text": term_org}},"functions": \
                        [{"script_score": {"script_id": "getTF","lang" : "groovy","params": {"term": term.lower(),"field": "text"}}}],"boost_mode": "replace"}},\
                        "size": corpus,"fields": ["docno"]})
        #results = es.search(index='ap_dataset_hw5',body={"query": {"match": {"text": term}},"explain": True,"size": 12316,"fields": ["docno"]})
        df=results['hits']['total']
        
        final_results = get_results(results)

        ttf = 0
        for k in range(len(final_results)):
            ttf+=final_results[k][1]
        
        for i in range(len(final_results)):
            doc_id = final_results[i][0]
            tf = final_results[i][1]            
            doc_no = final_results[i][2][0]
            doc_hash[doc_id] = doc_no
            dlen = dlen_hash[doc_id]            
              
            if doc_hash[doc_id] in okapi_score.keys():
                okapi_score[doc_hash[doc_id]]+=okapi_TF(tf, dlen, avg_dlen)
            else:
                okapi_score[doc_hash[doc_id]]=okapi_TF(tf, dlen, avg_dlen)
            
            if doc_hash[doc_id] in tf_idf_score.keys():
                tf_idf_score[doc_hash[doc_id]]+=okapi_TF(tf, dlen, avg_dlen)*(math.log((corpus/df)))
            else:
                tf_idf_score[doc_hash[doc_id]]=okapi_TF(tf, dlen, avg_dlen)*(math.log((corpus/df)))
            
            if doc_hash[doc_id] in bm25_score.keys(): 
                bm25_score[doc_hash[doc_id]]+=okapi_BM25(tf,dlen,avg_dlen,df,tf_query,corpus)
            else:
                bm25_score[doc_hash[doc_id]]=okapi_BM25(tf,dlen,avg_dlen,df,tf_query,corpus)                
            
    
        results = es.search(index='ap_dataset_hw5',body={"query": {"function_score": {"query": {"match_all": {}},"functions": \
                        [{"script_score": {"script_id": "getTF","lang" : "groovy","params": {"term": term.lower(),"field": "text"}}}],"boost_mode": "replace"}},\
                        "size": corpus,"fields": ["docno"]})

        #results = es.search(index='ap_dataset_hw5',body={"query": {"match_all": {}},"explain": True,"size": 12316,"fields": ["docno"]})
        
        final_results = get_results(results)        
                    
        for i in range(len(final_results)):
            doc_id = final_results[i][0]
            tf = final_results[i][1]
            doc_no = final_results[i][2][0]
            doc_hash[doc_id] = doc_no
            dlen = dlen_hash[doc_id]            
            
            if doc_hash[doc_id] in unigram_laplace_score.keys(): 
                unigram_laplace_score[doc_hash[doc_id]]+=unigram_laplace(tf,dlen)
            else:
                unigram_laplace_score[doc_hash[doc_id]]=unigram_laplace(tf,dlen)

            if doc_hash[doc_id] in unigram_jel_mer_score.keys(): 
                unigram_jel_mer_score[doc_hash[doc_id]]+=unigram_jel_mer(tf,dlen,(ttf-tf),(total_dlen-dlen))
            else:
                unigram_jel_mer_score[doc_hash[doc_id]]=unigram_jel_mer(tf,dlen,(ttf-tf),(total_dlen-dlen))
            
    for doc_id,doc_no in doc_hash.items():
        output+= str(query_id) + ' ' + str(doc_no)
        f1 = f2 = f3 = f4 = f5 = rel = 0
        if doc_no in okapi_score.keys():
            f1 = okapi_score[doc_no]
        if doc_no in tf_idf_score.keys():
            f2 = tf_idf_score[doc_no]
        if doc_no in bm25_score.keys():
            f3 = bm25_score[doc_no]
        if doc_no in unigram_laplace_score.keys():
            f4 = unigram_laplace_score[doc_no]
        if doc_no in unigram_jel_mer_score.keys():
            f5 = unigram_jel_mer_score[doc_no]
        if doc_no in relevance_hash[query_id].keys():
            rel = relevance_hash[query_id][doc_no]

        output+= ' ' + str(f1) + ' ' + str(f2) + ' ' + str(f3) + ' ' + str(f4) + ' ' + str(f5) + ' ' + str(rel) +'\n'
        
    file=open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\Testing_Matrix.txt",'a')
    file.write(output)
    file.close()
