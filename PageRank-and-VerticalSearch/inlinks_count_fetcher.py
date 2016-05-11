from pprint import pprint
import operator

file_name = "inlinks_count1.txt"
#file handle
file = open("C:\\Users\\hp\\Desktop\\IR_Documents\\"+file_name,"r")
#inlink dict to store inlinks of each url
inlink_dict = dict()

for line in file:
    url,count = line.split()
    inlink_dict[url]=int(count)

sorted_inlinks = sorted(inlink_dict.items(), key=operator.itemgetter(1), reverse=True)
print(inlink_dict['http://creativecommons.org/licenses/by-sa/3.0/'])
pprint(sorted_inlinks)
