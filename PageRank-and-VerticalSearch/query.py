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



def get_results(results):
    doc_details = {}
    for doc in results['hits']['hits']:
        doc_details[doc['_id']] = doc['_score']    
    return doc_details

es = elasticsearch.Elasticsearch("localhost:9200", timeout=10000, max_retries=10, revival_delay=0)

query_dict={"1":"data structur","2":"hash arrai","3":"spars matrix data structur","4":"implement queue"}
file_content=""
for queryNo,query in query_dict.items():
    print(query)
    body_cont = {
                    "size": 200,
                    "query":
                    {
                        "match":
                        {
                            "text": query
                        }
                    },
                    "explain": False	
                }
    
    results = es.search(index='k_dataset',body=body_cont)
    url_score_hash = get_results(results)
    rank=1
    for url in sorted(url_score_hash, key=url_score_hash.get, reverse=True):
        file_content+=str(queryNo)+' Q0 '+str(url)+' '+str(url_score_hash[url])+' Exp\n'
        rank+=1
file=open("C:\\Users\\hp\\Desktop\\IR_Documents\\Query_Scores.txt",'a')
file.write(file_content)
file.close()
