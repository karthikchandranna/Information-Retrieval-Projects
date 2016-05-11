import string
import re
import elasticsearch
import urllib3
import os
import math
import pickle
import time

es = elasticsearch.Elasticsearch()

files = os.listdir("C:\\Users\\SujithNarayan\\Desktop\\Study\\IR\\HW3\\Merge\\sujith_files")

# loading the inlink hash
inlink_hash = pickle.load(open("C:\\Users\\SujithNarayan\\Desktop\\Study\\IR\\HW3\\Merge\\inlinks_sujith","rb"))

for file in files:
    with open("C:\\Users\\SujithNarayan\\Desktop\\Study\\IR\\HW3\\Merge\\sujith_files\\"+file,'r',encoding='utf-8') as f:
        doc_file = f.read()
    print(file)
    docs=re.findall(r'<KCHAN_DOC>(.*?)</KCHAN_DOC>',doc_file,re.DOTALL)
    doc_hash = dict()
    if docs: 
        for doc in docs:

            #Extracting the tags in <KCHAN_DOC>            
            inlinks =''
            doc_no=re.findall(r'<KCHAN_DOCNO>(.*?)</KCHAN_DOCNO>',doc,re.DOTALL)[0]
            title=re.findall(r'<KCHAN_HEADING>(.*?)</KCHAN_HEADING>',doc,re.DOTALL)[0]
            headers=re.findall(r'<KCHAN_HEADERS>(.*?)</KCHAN_HEADERS>',doc,re.DOTALL)[0]
            text=re.findall(r'<KCHAN_CLEAN_FILE>(.*?)</KCHAN_CLEAN_FILE>',doc,re.DOTALL)[0]
            html=re.findall(r'<KCHAN_RAW_FILE>(.*?)</KCHAN_RAW_FILE>',doc,re.DOTALL)[0]
            outlinks=re.findall(r'<KCHAN_OUTLINKS>(.*?)</KCHAN_OUTLINKS>',doc,re.DOTALL)[0]

            # Getting the inlinks of this doc
            if doc_no in inlink_hash.keys():
                inlinks_list = inlink_hash[doc_no]
                set_inlinks = set(inlinks_list)                
                inlinks = '|'.join(map(str, set_inlinks))

            # Removing binary bits
            html = html[2:]
            html = html[:-1]            

            # Check if the url exists in the index
            if es.exists(index="k_chan", doc_type="document", id=doc_no) == True:

                results = es.get(index='k_chan',doc_type="document",id=doc_no)
                existing_inlinks = results['_source']['inlinks']
                existing_inlinks_list = existing_inlinks.split("|")
                set_existing_inlinks = set(existing_inlinks_list)

                new_inlinks = ''
                new_inlinks_set = set()

                # Merge the inlinks already in the index with the new inlinks from the file
                if len(set_existing_inlinks) > 0:
                    new_inlinks_set = set_existing_inlinks.union(set_inlinks)
                    new_inlinks = '|'.join(map(str, new_inlinks_set))

                else:
                    new_inlinks = inlinks

                # Create a new body with new set of inlinks
                new_body = {
                    "script" : "ctx._source.inlinks = new_inlinks",
                    "params": {
                        "new_inlinks": new_inlinks 
                        }
                    }

                # Update the index
                es.update(index='k_chan',doc_type="document",id=doc_no, body=new_body)
                es.indices.refresh(index='k_chan')

            else:
                # New url to be added to the index                
                doc_body = {
                    'doc_no': doc_no,
                    'title': title,
                    'headers': headers,
                    'text': text,
                    'html_Source': html,
                    'outlinks': outlinks,
                    'inlinks':inlinks}
            
                es.index(index="k_chan", doc_type='document', id=doc_no, body=doc_body)
