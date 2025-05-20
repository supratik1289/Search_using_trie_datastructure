import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)
import pandas as p
import time
import pickle
from unidecode import unidecode

#opening and reading all the data from the corpus

a = time.time()
df = p.read_excel("wiki_movie_plots_deduped.xlsx")
df = df.drop(columns=["Release Year","Origin/Ethnicity","Director","Cast","Genre"]) #drops unimportant fields


#storing essential data
title = df["Title"]
plot = df["Plot"]
link = df["Wiki Page"]

l = time.time()
b = time.time()
print("Total reading to data frame time: ",b-a) #measuring time taken for performance judging purposes

#pickling the unedited data to get back original results during search
a = time.time()

with open("dataframe","wb") as f:
    pickle.dump((title,plot,link),f)

b = time.time()
print("Time required to pickle the dataframe: ",b-a)

#preprocessing the data 

NDOC = len(title)
print("Number of documents to be processed:",NDOC)

symbols = ['`','~','!','@','#','$','%','^','&','*','(',')','_','-','+','=','{','[','}','}','|',':',';','"',"'",'<',',','>','.','?','/',']','\n','\0','1','2','3','4','5','6','7','8','9','0']

def preprocess(x):
    y = ''
    x_iter = iter(x) 
    for a in x_iter:
        if (a not in symbols): 
            y = y+unidecode(a.lower())
    return y

a = time.time()

#preprocessing title and plot 

for i in range(len(title)):
    title[i] = preprocess(str(title[i]))

for i in range(len(plot)):
    plot[i] = preprocess(str(plot[i]))

b = time.time()
print("Total Pre-processing time: ",b-a)

#trie structure definition

class Node:
    def __init__(self, postings): #initialize a node
        #each node has a postings list for a word ending this node and a children list with link to next 26 letters
        self.postings = []
        self.children = [None for a in range(27)]
    def insert(self,word,docid): #insert a word in the trie by creating suitable number of nodes and also update the postings list
        a = list(word) 
        if a!=[]: 
            if self.children[ord(a[0])-97] == None:
                self.children[ord(a[0])-97] = Node([])
                s = a.pop(0) 
                self.children[ord(s)-97].insert("".join(a),docid) 
            else:
                #print(ord(a[0])-97)
                s = a.pop(0)
                self.children[ord(s)-97].insert("".join(a),docid)
        else: 
            if self.postings == []:
                self.postings.append(docid)
            elif docid != self.postings[len(self.postings)-1]:
                self.postings.append(docid)
    def search(self,word): #search the word by travelling down the trie and retrieve the postings list
        """
        if self.children == ['' for a in range(27)]:
            return ['Result Not Found']
        else:
        """
        a = list(word) 
        if a == []: 
            return self.postings
        else:
            if self.children[ord(a[0])-97] != None: 
                s = a.pop(0)
                return self.children[ord(s)-97].search("".join(a))
            else:
                return ['Result Not Found'] 

#trie initialization

head = Node([])
head1 = Node([])
head2 = Node([])
#forming the tries for different fields

s = time.time()

for i in range(NDOC):
    x = title[i].split(" ")
    y = plot[i].split(" ")
    if i%500==0:
        print(i,"documents processed")
    for a in x:
        try:
            head.insert(a,i)
            head1.insert(a,i)
        except:
            continue
    for a in y:
        try:
            head.insert(a,i)
            head2.insert(a,i)
        except:
            continue
"""
for i in range(NDOC):
    x = plot[i].split(" ")
    if i%500==0:
        print(i,"documents processed")
    for a in x:
        try:
            head.insert(a,i)
            head2.insert(a,i)
        except:
            continue
"""
b = time.time()

print("Trie formation time:",b-s)

#converting the trie into a convenient structure to store it
def pickle_tree(node):
    if node is None:
        return None
    return (node, [pickle_tree(child) for child in node.children])

a = time.time()
#pickling the trees to a file
pickeled_tree = pickle_tree(head)
with open("moviedata", "wb") as f:
    pickle.dump(pickeled_tree, f)

pickeled_tree = pickle_tree(head1)
with open("moviedata_title", "wb") as f:
    pickle.dump(pickeled_tree, f)

pickeled_tree = pickle_tree(head2)
with open("moviedata_plot", "wb") as f:
    pickle.dump(pickeled_tree, f)

b = time.time()
print("Trie Pickling time:",b-a)

print("Total time taken:",time.time()-l)
