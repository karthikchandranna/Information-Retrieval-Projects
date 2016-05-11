import string
import re
from elasticsearch import elasticsearch
import urllib3
import os
import math

es = elasticsearch.Elasticsearch("localhost:9200", timeout=10000, max_retries=10, revival_delay=0)

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
            li_texts=re.findall(r'<TEXT>(.*?)</TEXT>',doc,re.DOTALL)
            doc_no= ''.join(map(str, li_doc_no))
            texts=''.join(map(str, li_texts))
            doc_body = {
                    'docno': doc_no,
                    'text': texts}
            es.index(index="ap_dataset", doc_type='document', id=i, body=doc_body)
            doc_hash[doc_no]=texts
            i+=1
for key in sorted(doc_hash):
    print (key,":", doc_hash[key])
