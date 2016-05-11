import sys
import collections
import math

#checking for -q option
cmd_flag = 0
if len(sys.argv) >= 2:
    if (sys.argv[1] == '-q'):
        cmd_flag = 1
        
#QREL file name
f_name = "qrels.adhoc.51-100.AP89.txt"
#Qrel file open
file = open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\"+f_name,'r')
#dict for Qrel qrel_dict[query_id][url][grade1,grade2,grade3]
qrel_dict = collections.OrderedDict()
#dict for relevant urls in qrel .ie grade 1 or 2
qrel_rel_dict = collections.OrderedDict()
#dict for list of grades for every query
grade_dict = collections.OrderedDict()
#every line in Qrel file
for line in file:
    #split by space
    fields = line.split()
    #retrieve queryid, assessor,url and grade
    query_id = fields[0]
    assessor = fields[1]
    url = fields[2]
    grade = int(fields[3])
    #storing grade in binary
    grade_binary = 0
    if grade>0:
        grade_binary=1
    #taking all urls for a query from dict
    if query_id in qrel_dict.keys():
        url_dict = collections.OrderedDict()
        url_dict = qrel_dict[query_id]
	#assigning the grade to the current url
        if url in url_dict.keys():
            url_dict[url].append(grade_binary)
        else:
            url_dict[url] = [grade_binary]
	#repacking qrel dict
        qrel_dict[query_id] = url_dict
	#assigning grade to the url 
    else:
        qrel_dict[query_id] = collections.OrderedDict()
        url_grade_dict = collections.OrderedDict()
        url_grade_dict[url] = [grade_binary]
        qrel_dict[query_id] = url_grade_dict

    #dict to store list of grades for every query
    if query_id in grade_dict.keys():
        url1_dict = collections.OrderedDict()
        url1_dict = grade_dict[query_id]
	#assigning the grade to the current url
        if url in url1_dict.keys():
            url1_dict[url].append(grade)
        else:
            url1_dict[url] = [grade]
	#repacking qrel dict
        grade_dict[query_id] = url1_dict
	#assigning grade to the url 
    else:
        grade_dict[query_id] = collections.OrderedDict()
        url1_grade_dict = collections.OrderedDict()
        url1_grade_dict[url] = [grade]
        grade_dict[query_id] = url1_grade_dict
        
    #maintaining dict to store number of relevant urls for each query
    if query_id in qrel_rel_dict.keys():
        qrel_rel_dict[query_id] += grade_binary
    else:
        qrel_rel_dict[query_id] = grade_binary
    
    
#each query,url combo will have 3 grades. Aggregating them as 1 grade
for query_id in qrel_dict.keys():
    for url in qrel_dict[query_id].keys():
        grades = qrel_dict[query_id][url]
	#qrel_dict[query_id][url]= aggregated grade
        qrel_dict[query_id][url] = max(set(grades), key=grades.count)


#each query,url combo will have 3 grades. Aggregating them as 1 grade
for query_id in grade_dict.keys():
    for url in grade_dict[query_id].keys():
        grades = grade_dict[query_id][url]
	#grade_dict[query_id][url]= aggregated grade
        grade_dict[query_id][url] = max(set(grades), key=grades.count)

file.close()
#query score file name
scores_file_name = "Okapi_BM_25_Scores.txt"

#query score file
scores_file_handle = open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\"+scores_file_name,'r')

#query result dict to store queries and its list of urls 
query_result_dict = collections.OrderedDict()

#every line in score file
for line in scores_file_handle:
    #splitting fields and retrieving query id, url
    scores_fields_list = line.split()	
    query_id = scores_fields_list[0]
    url = scores_fields_list[2]
    #adding list of urls to that query id
    if query_id in query_result_dict.keys():
        query_result_dict[query_id].append(url)
    else:
        query_result_dict[query_id] = [url]  

scores_file_handle.close()

#precision_dict[query_id]= list of precision values at each k value
precision_dict = collections.OrderedDict()

#recall_dict[query_id]= list of recall values at each k value
recall_dict = collections.OrderedDict()

#avg_prec_dict[query_id]= average precision value of each query
avg_prec_dict = collections.OrderedDict()

#values_array_dict[query_id]= list of grades of each url
values_array_dict = dict()

#sum of precision at cutoff values
sum_prec_cutoffs = dict()

#sum of recalls at cutoff values
sum_recalls_cutoffs = dict()

sum_prec_recalls = []

#the sum of avg precision of every query
sum_avg_precs = 0

#sum of r precision of every query
sum_r_prec = 0

#cutoff where scores are required. offset by 1 as index starts from 0 not 1
cutoffs= [4,9,19,49,99]

#recalls where interpolated precision scores are required.
recalls = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

#every query in scores dict
for query_id in query_result_dict.keys():
    #number of retrieved urls
    no_ret=0
    #number of relevant urls which where retrieved
    no_rel_ret = 0
    #number of relevant urls for this query
    no_relevant = qrel_rel_dict[query_id]
    #sum of precisions for each url for this query
    sum_prec = 0
	
    #list of grades of all urls for this query
    values_array_query = []
	
    #every url for this query
    for url in query_result_dict[query_id]:
	#incrementing number of retrieved 
        no_ret += 1    
	#incrementing number of relevant retrieved if grade > 0
        if query_id in qrel_dict.keys():
            if url in qrel_dict[query_id].keys():
                if qrel_dict[query_id][url] >= 1:
                    sum_prec +=  (1 + no_rel_ret)/no_ret
                    no_rel_ret += 1

        if query_id in grade_dict.keys():
            if url in grade_dict[query_id].keys():
                values_array_query.append(grade_dict[query_id][url])

        #precision@k is relevant retrieved by retrieved(k)    
        precision = no_rel_ret/no_ret

        #adding this precision value to dict
        if query_id in precision_dict.keys():
            precision_dict[query_id].append(precision)
        else:
            precision_dict[query_id] = [precision]

        #recall@k is relevant retrieved by relevant         
        recall = no_rel_ret/no_relevant

        #adding this recall value to dict
        if query_id in recall_dict.keys():
            recall_dict[query_id].append(recall)
        else:
            recall_dict[query_id] = [recall]

    values_array_dict[query_id] = values_array_query

    #looping for 5,10,20,50,100 urls
    for cutoff in cutoffs:
        if cmd_flag == 1:
            print ("Precision for query number-",query_id,"at k",cutoff+1,":",precision_dict[query_id][cutoff])
            print ("Recall for query number-",query_id,"at k",cutoff+1,":",recall_dict[query_id][cutoff])
            f1_denom = (precision_dict[query_id][cutoff]+recall_dict[query_id][cutoff])
            if f1_denom>0:
                f1_cutoff = (2 * precision_dict[query_id][cutoff] * recall_dict[query_id][cutoff])/f1_denom
            else:
                fi_cutoff = 0
            print ("F-measure for query number-",query_id,"at k",cutoff+1,":",f1_cutoff)
            
        #calculating sum of precision at the cut-offs
        if cutoff in sum_prec_cutoffs.keys():
            sum_prec_cutoffs[cutoff] += precision_dict[query_id][cutoff]
        else:
            sum_prec_cutoffs[cutoff] = precision_dict[query_id][cutoff]
        #calculating sum of recall at the cut-offs
        if cutoff in sum_recalls_cutoffs.keys():
            sum_recalls_cutoffs[cutoff] += recall_dict[query_id][cutoff]
        else:
            sum_recalls_cutoffs[cutoff] = recall_dict[query_id][cutoff]

    #calculating avg precision for the query and then storing in dict
    avg_precision = sum_prec/no_relevant
    avg_prec_dict[query_id] = avg_precision
    #calculating sum of these avg precs
    sum_avg_precs += avg_precision
    #all relevant retrieved by all relevant - at k=200
    final_recall = no_rel_ret/no_relevant

    #printing precision and recall for every query
    if cmd_flag == 1:
        print ("Precision Avg for query number-",query_id,":",avg_prec_dict[query_id])
        print ("Recall Avg for query number-",query_id,":",final_recall)

    #populating precision and recall from 200 to 1000
    for i in range(no_ret+1,1001):
        precision_dict[query_id].append(no_ret/i)
        recall_dict[query_id].append(final_recall)

    #calculating r precision
    if no_relevant > no_ret:
        r_prec = final_recall
    else:
        #precison of the query when k = number of relevant urls
        r_prec = precision_dict[query_id][no_relevant-1]
    #printing r precision
    if cmd_flag == 1:
        print ("R-precision for query number-",query_id,"is",r_prec)
    #sum of r precision        
    sum_r_prec += r_prec

    #Now calculate interpolated precisions
    max_prec = 0
    #prec_list = precision_dict[query_id]
    for i in range(999,-1):
        if (precision_dict[query_id][i] > max_prec):
             max_prec = precision_dict[query_id][i]
        else:
            precision_dict[query_id][i] = max_prec

    #calculate precision at recall levels
    prec_at_recalls = []
    i = 0
    #for every recall
    for recall in recalls:
        #checking if recall@i is less than recall value
        while (i <= 999 and recall_dict[query_id][i] < recall):
            i+=1
        #once i is found where recall@i = recall, find precision@i
        if (i <= 999):
            prec_at_recalls.append(precision_dict[query_id][i])
        #if i is not found, precision is 0
        else:
            prec_at_recalls.append(0)

    #finding sum of precision at recalls      
    for i in range(0,len(recalls)):
        if i<len(sum_prec_recalls):
            sum_prec_recalls[i] += prec_at_recalls[i]
        else:
            sum_prec_recalls.append(prec_at_recalls[i])

grades = []
n_dcg_dict = dict()
sum_n_dcg = 0
for query_id in values_array_dict.keys():
    #list of grades
    grades = values_array_dict[query_id]
    #grade of 1st url
    dcg = grades[0]

    #dcg = grade1 + sumof(grade[i]/log(i+1))
    for i in range(1,len(grades)):
        dcg += (grades[i]/math.log(i+1))

    #sort the grades
    grades.sort(reverse=True)
    #highest grade
    sorted_dcg = grades[0]
    n_dcg = 0
    if sorted_dcg>0:
        #sorted_dcg = grade1 + sumof(grade[i]/log(i+1))
        for i in range(1,len(grades)):
            sorted_dcg += (grades[i]/math.log(i+1))
        #n_dcg is ratio of dcg abd sorted dcg 
        n_dcg = dcg/sorted_dcg
        if cmd_flag == 1:
            print("n-DCG for query number-",query_id,"is",n_dcg)
    sum_n_dcg += n_dcg
    
#number of queries
no_queries = len(query_result_dict.keys())
#average n dcg  
avg_n_dcg = sum_n_dcg/no_queries  
#finding average precision at recalls
for i in range(0,len(recalls)):
  avg_prec_at_recalls = sum_prec_recalls[i]/no_queries
  print ("Interpolated Recall - Precision Average at",recalls[i],"\t",avg_prec_at_recalls)

#for 5,10,20,50,100
for cutoff in cutoffs:

    #avg precision across all queries at k
    avg_prec_cutoff = sum_prec_cutoffs[cutoff]/no_queries
    print ("Precision at",cutoff+1,"docs-",avg_prec_cutoff)

    #avg recall across all queries at k
    avg_recall_cutoff = sum_recalls_cutoffs[cutoff]/no_queries
    print ("Recall at",cutoff+1,"docs-",avg_recall_cutoff)

    #avg F1 measure across all queries at k
    avg_f1_cutoff = (2 * avg_prec_cutoff * avg_recall_cutoff)/(avg_prec_cutoff+avg_recall_cutoff)
    print ("F-measure at",cutoff+1,"docs-",avg_f1_cutoff)

#overall avg precision across all queries
final_avg_precision = sum_avg_precs/no_queries
print ("Average Precision value-",final_avg_precision)

#overall avg R precision across all queries
avg_r_prec = sum_r_prec/no_queries
print ("R-Precision value-",avg_r_prec)

#overall avg nDCG across all queries
print ("nDCG value-",avg_n_dcg)
 
