import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)
import pandas as p
import time
import pickle
from unidecode import unidecode

start = time.time()

with open("dataframe","rb") as f: #load the dataframe to fetch original information for user
    data = pickle.load(f)

title = data[0] 
plot = data[1]
link = data[2]

NDOC = len(title)

symbols = ['`','~','!','@','#','$','%','^','&','*','(',')','_','-','+','=','{','[','}','}','|',':',';','"',"'",'<',',','>','.','?','/',']','\n','\0','1','2','3','4','5','6','7','8','9','0']

def preprocess(x):
    y = ''
    x_iter = iter(x) 
    for a in x_iter:
        if (a not in symbols): 
            y = y+unidecode(a.lower())
    return y

#defining trie structure so that we can unpickle the information and use it

class Node:
    def __init__(self, postings):
        self.postings = []
        self.children = [None for a in range(27)]
    def insert(self,word,docid):
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
    def search(self,word):
        a = list(word)
        if a == []:
            return self.postings
        else:
            if self.children[ord(a[0])-97] != None:
                s = a.pop(0)
                return self.children[ord(s)-97].search("".join(a))
            else:
                return ['Result Not Found']

#loading the pickeled trie

with open("moviedata", "rb") as f:
    loaded_tree = pickle.load(f)

head = loaded_tree[0]

with open("moviedata_title", "rb") as f:
    loaded_tree = pickle.load(f)

head1 = loaded_tree[0]

with open("moviedata_plot", "rb") as f:
    loaded_tree = pickle.load(f)

head2 = loaded_tree[0]

#running the engine

end = time.time()

print("Search Engine Initialization time:",end-start)

print("\n\nSupratik's Rudimentary Search Engine: ")
print("Options: ")
print("Enter 1 for Searching.")
print("Enter 2 to Quit.")

while(1):
    try:
        service = int(input("Enter Option: "))
        if service == 1:
            query = input("Enter Query: ").split()
            print()
            num = int(input("Enter Max Number of Results to Show: "))
            field = int(input("Input in which fields to search:\n1 for Title\n2 for Plot\n3 for both\nOption: "))
            s = time.time()
            a=[]
            if field==1:
                a = set(head1.search(preprocess(query[0])))
                for x in query:
                    a = a.intersection(set(head1.search(preprocess(x))))
                a = list(a)
            elif field==2:
                a = set(head2.search(preprocess(query[0])))
                for x in query:
                    a = a.intersection(set(head2.search(preprocess(x))))
                a = list(a)
            else:
                a = set(head.search(preprocess(query[0])))
                for x in query:
                    a = a.intersection(set(head.search(preprocess(x))))
                a = list(a)
            print("\nSearched through %d documents in %1.10f seconds" %(NDOC,time.time()-s))
            print()
            if a!= ['Result Not Found'] and a!=[]:
                for i in range(min((num),len(a))):
                    print(title[a[i]])
                    print(link[a[i]])
                    print(plot[a[i]][0:50]+"...")
                    print()
            else:
                print("No Results Could be Found:(")
        elif service == 2:
            break
        else:
            print("Invalid Request!")
    except:
        print("Invalid Request!")