"""
    All the preprocessing before building the indexes

"""
from tkinter import Tk
import csv
import string
import math
import datetime
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

csvrows=[]
songs = {}
terms = {}
numDoc = 2000

def printDuration(starttime):
    # retrieval time
    endtime = datetime.datetime.now()
    print("End time",str(endtime))
    diff = endtime-starttime
    print("Time taken to retrieve:",diff.seconds,"seconds or ",diff.microseconds," microseconds")

def intersection(lst1, lst2):
    # Use of hybrid method
    temp = set(lst2)
    lst3 = [value for value in lst1 if value in temp]
    return lst3

def tokenize(str):
    #tokens = word_tokenize(str)
    #stop_words = set(stopwords.words('english'))  # change this no need of stop words or calculate stop words from corpus
    word_tokens = word_tokenize(str)
    only_alpha = [c for c in word_tokens if c not in string.punctuation]
    if not only_alpha :
        return []
    filtered_tokens = only_alpha# [w for w in only_alpha if not w in stop_words]
    no_chars = [w for w in only_alpha if not any(char.isdigit() for char in w)] ## this doesn't seem to be working
    return filtered_tokens

def stem(tokens):
    ps = PorterStemmer()
    stem_tokens=[]
    s_dict = {}
    pos=0
    for t in tokens:
        st = ps.stem(t)
        stem_tokens.append(st)              ##append needed???
        if st in s_dict.keys():
            s_dict[st][0]= s_dict[st][0] + 1 #termfrequency
            s_dict[st][1].append(pos)
        else:
            s_dict[st] = [1,[pos]]
        pos=pos+1
    return stem_tokens,s_dict

def calculate_Tf_Idf(terms):
    for term in terms:
        termdict = terms[term][2]
        for doc in termdict:
            termdict[doc][1] = termdict[doc][0] * math.log((numDoc/terms[term][1]),10)    #tf*idf
