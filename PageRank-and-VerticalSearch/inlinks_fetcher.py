from elasticsearch import elasticsearch
from pprint import pprint
import collections

def get_results(results):
    inlinks_hash = collections.OrderedDict()
    count = 0
    for doc in results['hits']['hits']:
        count += 1
        inlinks_non_split = doc['fields']['inlinks']
        inlinks = inlinks_non_split[0].split('|')
        inlinks_hash[doc['_id']] = inlinks
    return inlinks_hash


def write_to_file(inlinks_hash):    
    file=open("C:\\Users\\hp\\Desktop\\IR_Documents\\inlinks.txt",'a')
    file_content = ''
    for base_link,inlinks in inlinks_hash.items():
        file_content += str(base_link)
        for inlink in inlinks:
            file_content += ' ' + str(inlink)
        file_content += '\n'
    file.write(file_content)
    file.close()

def write_count(inlinks_hash):    
    file=open("C:\\Users\\hp\\Desktop\\IR_Documents\\inlinks_count1.txt",'a')
    file_content = ''
    for base_link,inlinks in inlinks_hash.items():
        file_content += str(base_link) + ' ' + str(len(inlinks)) + '\n' 
        
    file.write(file_content)
    file.close()

es = elasticsearch.Elasticsearch("localhost:9200", timeout=10000, max_retries=10, revival_delay=0)
results = es.search(index="k_dataset", body={"query": {"match_all": {}}})
no_docs = results['hits']['total']
print(no_docs)
i=0
while i<(no_docs-1000):    
    results = es.search(index='k_dataset',body={"fields": "inlinks","size": 1000,"from": i})
    inlinks_hash = collections.OrderedDict()
    inlinks_hash = get_results(results)
    write_count(inlinks_hash)
    #write_to_file(inlinks_hash)
    print("Wrote inlinks from",i,"to", i+1000) 
    i += 1000

results = es.search(index='k_dataset',body={"fields": "inlinks","size": 1000,"from": i})
inlinks_hash = collections.OrderedDict()
inlinks_hash = get_results(results)
write_count(inlinks_hash)
#write_to_file(inlinks_hash)
print("Wrote inlinks from",i,"to", no_docs)
#sorting the dict based on page rank in descending order
#sorted_page_rank = sorted(page_rank_dict.items(), key=operator.itemgetter(1), reverse=True)

        
