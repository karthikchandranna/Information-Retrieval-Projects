import string
import re
from elasticsearch import elasticsearch
import urllib3
import os
import math

def get_relevant_docs():
    file_name = 'qrels.adhoc.51-100.AP89.txt'
    file = open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\"+file_name,"r")
    docs_set = set()
    for line in file:
        fields = line.split()
        doc_no = fields[2]
        docs_set.add(doc_no)
    return docs_set    
    

es = elasticsearch.Elasticsearch("localhost:9200", timeout=10000, max_retries=10, revival_delay=0)
rel_docs_set = get_relevant_docs()
print("Relevant docs:",str(len(rel_docs_set)))
files = os.listdir("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\ap89_collection")
i=1

for file in files:
    with open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\ap89_collection\\"+file) as f:
        doc_file = f.read()
    print(file)
    docs=re.findall(r'<DOC>(.*?)</DOC>',doc_file,re.DOTALL)
    doc_hash = dict()
    if docs:
        for doc in docs:
            li_doc_no=re.findall(r'<DOCNO>(.*?)</DOCNO>',doc)            
            doc_no= ''.join(map(str, li_doc_no))
            doc_no = doc_no.strip()
            if doc_no in rel_docs_set:
                li_texts=re.findall(r'<TEXT>(.*?)</TEXT>',doc,re.DOTALL)
                texts=''.join(map(str, li_texts))
                doc_body = {
                        'docno': doc_no,
                        'text': texts}
                es.index(index="ap_dataset_hw5", doc_type='document', id=i, body=doc_body)
                doc_hash[doc_no]=texts
                i+=1
print(str(i-1),"Documents uploaded to elasticsearch")
