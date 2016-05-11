from pprint import pprint
import operator

#file name
file_name = "wt2g_inlinks.txt"
#file handle
file = open("C:\\Users\\hp\\Desktop\\IR_Documents\\"+file_name,"r")
#inlink dict to store inlinks of each url
inlink_dict = dict()
#outlink dict to store outlinks of each url
outlink_dict = dict()
#page rank dict to store the oage rank of each url
page_rank_dict = dict()

#for every line in file
for line in file:
    urls = line.split()
    base_url = urls[0]

    #extracting the inlinks of the base url
    inlinks = []
    if len(urls) > 1:
        inlinks = urls[1:]    
    inlink_dict[base_url] = inlinks

    #incrementing the outlinks count of every url whichh are inlinks of the base_url
    for link in inlinks:
        if link in outlink_dict.keys():
            outlink_dict[link] += 1
        else:
            outlink_dict[link] = 1

    #initializing pagerank of the urls in the line as 0. 
    for url in urls:
        page_rank_dict[url] = 0     

file.close()
#number of pages in the pagerank dict
no_pages = len(page_rank_dict.keys())
#damping factor
d_factor = 0.85

# assigning 1/n as page rank at 1st iteration
for page in page_rank_dict.keys():
    page_rank_dict[page] = 1/no_pages
#flag to determine end of program
halting_flag = True
while halting_flag:
    
    halting_flag = False
    #every page in page rank dict
    for page in page_rank_dict.keys():
        #inlinks of the current page
        inlinks = inlink_dict[page]
        page_rank = 0
        #computing summation of ratio of page_rank/outlinks for all inlinks
        for inlink in inlinks:
            page_rank += (page_rank_dict[inlink]/outlink_dict[inlink])
        #mutliplying damping factor
        page_rank = (d_factor * page_rank)
        #page_rank value for 1st inlink
        page_rank += ((1-d_factor)/no_pages)
        #checking if previous iteration and current iteration gives almost the same page rank
        if abs(page_rank - page_rank_dict[page]) > 0.0001:
            halting_flag = True
            
        page_rank_dict[page] = page_rank
#sorting the dict based on page rank in descending order
sorted_page_rank = sorted(page_rank_dict.items(), key=operator.itemgetter(1), reverse=True)

#writing to file
file = open("C:\\Users\\hp\\Desktop\\IR_Documents\\Page_Ranks.txt","a")
content = ""
for page, value in sorted_page_rank:
    content += str(page)+" : "+str(value)+"\n"
    
file.write(content)
file.close()
