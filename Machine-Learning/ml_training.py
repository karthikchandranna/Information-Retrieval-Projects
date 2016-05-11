from sklearn import tree
from sklearn import linear_model
from pprint import pprint
import collections
import operator

train_f_name = "Training_Matrix.txt"
training_file = open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\"+train_f_name,"r")
X = []
Y = []
for line in training_file:
    fields = line.split()
    features = [float(x) for x in fields[2:7]]
    X.append(features)
    Y.append(int(fields[-1]))
training_file.close()

#clf = tree.DecisionTreeClassifier()
clf = linear_model.LinearRegression()
clf = clf.fit(X, Y)

test_f_name = "Testing_Matrix.txt"
testing_file = open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\"+test_f_name,"r")
test = []
score_hash = collections.OrderedDict()
for line in testing_file:
    fields = line.split()
    query_id = fields[0]
    doc_no = fields[1]
    features = [float(x) for x in fields[2:7]]
    out = clf.predict([features])
    if query_id in score_hash.keys():
            score_hash[query_id][doc_no] = float(out[0])
    else:
            score_hash[query_id] = collections.OrderedDict()
            score_hash[query_id][doc_no] = float(out[0])
testing_file.close()

for query_id in score_hash.keys():
    content=''
    sorted_score_hash_query = sorted(score_hash[query_id].items(), key=operator.itemgetter(1), reverse=True)
    rank=1
    for ele in sorted_score_hash_query:
        content+=str(query_id)+' Q0 '+ele[0]+ ' '+ str(rank)+' '+str(ele[1])+' Exp\n'
        rank+=1

    file=open("C:\\Users\\hp\\Desktop\\IR_Documents\\AP_DATA\\Testing_Scores1.txt",'a')
    file.write(content)
    file.close()
