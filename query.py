"""
    All methods related to query processing
"""
from tkinter import Tk
from preprocessing import tokenize,stem,intersection,printDuration
#from heapq import heappop,_heapify_max
from indexing import create_connection
import sqlite3
import pickle
import datetime
class selSong:
    """Objects of this type represent the selected
       songs during query processing.Contains methods
       to build and process them
    """

    def __init__(self,id,termscores):
        """ updates id and scores"""
        self.id = id
        self.score = 0
        for term in termscores:
            self.updateScore(termscores[term])
        self.songdetails = {}

    def updateDetails(self,details):
        self.songdetails = details

    def updateScore(self,val):
        self.score = self.score+val

    def __lt__(self, other):
        """for ranking song objects happens based on score"""
        return (self.score < other.score)

class Query:
    """Objects of this type represent the query under consideration
       Methods helps in processing the query
    """

    def __init__(self,qtext):
        self.queryText = qtext
        self.queryResult = []
        self.noResult = None
        self.topSearch = None
        self.advSearch = None
        self.advOptions = {}
        self.queryEngine = None
        self.weights = {"all":2,"p":2,"n":2,"a":2,"y":2,"g":2}
        self.curweight = 1

    def getIndexes(self,tokens,cond = 0,pos=0):
        """fetches all the terms,docid and score from termdoc
           Arguments:
            tokens -- normalized query tokens ,
            cond --{0,1} 0- union i.e should contain all query terms,
                    1 - intersection, all query term should be present
            false --{0,1} 0- postion index requierd otherwise 1
           return:
            a dictionary {docid:{<term>:<score>}}
        """
        docs ={}
        conn = create_connection(self.queryEngine.dbfile)
        cur = conn.cursor()
        questionmarks = '?' * len(tokens)
        if pos == 1:
            querystr = """SELECT term,docid,dscore,posList FROM termdoc WHERE
                            term IN ({})""".format(','.join(questionmarks))
        else:
            querystr = """SELECT term,docid,dscore FROM termdoc WHERE
                            term IN ({})""".format(','.join(questionmarks))
        cur.execute(querystr,tokens)
        for row in cur:
            if pos == 1:
                termval = [row[2],row[3]] # score, postions
            else:
                termval = row[2] #only score
            term = row[0]
            if row[1] in docs.keys():
                docs[row[1]].update({term:termval})
            else:
                docs[row[1]] = {term:termval}

        if cond == 1:
            for k in list(docs.keys()):  ## filtering for and condition
                if len(docs[k]) < len(tokens):#delete if number of terms less than that of tokens
                    del docs[k]
        conn.close()
        return docs

    def getSongDetails(self,song,conn):
        """fetches details of the selected song object
           Arguments:
           song -- song object to fetched
           conn -- current database connection
        """
        cur = conn.cursor()
        querystr = "SELECT * FROM songs WHERE id = ?"
        cur.execute(querystr,(song.id,))
        row = cur.fetchall()
        songdict = {}
        cols = [des[0] for des in cur.description]
        songdict = dict(zip(cols,row[0]))
        songdict.pop(cols[0],None)  # don't need the ids
        song.updateDetails(songdict)

    def queryProcessing(self,engine):
        """query processing for basic Search
            Arguments:
                engine -- object to which the Query object belongs
        """
        self.queryEngine = engine
        print("*********Query processing********")
        starttime = datetime.datetime.now()
        print("Start time",str(starttime))
        print("Query---",self.queryText)

        q_tokens = tokenize(self.queryText)  #tokenize queryText
        qs_tokens,qs_dict = stem(q_tokens)

        if len(qs_tokens) == 0:
            #engine.noResult = True
            self.noResult = True #choose one
            return

        # all the documents that contain any of the terms
        querydocs = self.getIndexes(qs_tokens)

        #Ranking based on score
        songHeap = []
        for doc in querydocs: #scoring document at a time
            song = selSong(doc,querydocs[doc])
            songHeap.append(song)

        if len(songHeap)==0:
            #engine.noResult = True
            self.noResult = True
            return

        self.queryResult = songHeap
        songHeap.sort(reverse=True)
        #Fetching song details
        start=0
        count = None
        if self.topSearch == True:
            count = 1
        else:
            count = engine.displayLength
        self.nextSongListPrep(0,count)

        # retrieval time
        printDuration(starttime)

    def nextSongListPrep(self,startidx,endidx):
        """Updates the song details from database for the next
            list of enteries to be displayed in the given range
            :startidx --start index in the song object
            :endidx -- end index in the song object list
        """
        conn = create_connection(self.queryEngine.dbfile)
        if endidx > len(self.queryResult):
            endidx = len(self.queryResult)
        for i in range(startidx,endidx):
            self.getSongDetails(self.queryResult[i],conn)
        conn.close()

    def filterName(self,conn,docs=None,onlyN = False):
        """filters song documents based on the details of song name given
            song name is a wildcard query.If not query text exists.ALl songs
            matching the name are given
            : docs -- dictionary of selected docs till now
                      returns list of docids in that case
            :onlyN -- means this is the only seletion criteria
        """
        cur = conn.cursor()
        options = self.advOptions
        labels =[]
        label = options["songname"]
        if label !='':
            labels =["$"+label]  ## starts with
        label = options["songend"]
        if label !='':
            labels.append(label+"$")  ## end with
        if onlyN == True:  # no query text
            labeldocs = []
            for label in labels:
                cur.execute("SELECT docid FROM permName where key = ? ",(label,))
                row = cur.fetchall()
                if(len(row)<1):
                    return
                pickled = row[0][0]
                docids = pickle.loads(pickled)
                labeldocs.append(docids)
            if len(labels) == 1:
                return labeldocs[0]
            else:
                return intersection(labeldocs[0],labeldocs[1])
        elif len(docs) > 0:
            seldocids = list(docs.keys())
            labeldocs = []
            for label in labels:
                cur.execute("SELECT docid FROM permName where key = ? ",(label,))
                row = cur.fetchall()
                if(len(row)<1):
                    return
                pickled = row[0][0]
                docids = pickle.loads(pickled)
                labeldocs.append(docids)
            if len(labels) == 1:
                docids= labeldocs[0]
            else:
                docids= intersection(labeldocs[0],labeldocs[1])
            for id in seldocids:  ## filtering on name
                if id not in docids:
                    del docs[id]

    def filterArtist(self,conn,docs=None,onlyA = False):
        """filters song documents based on the details of artist name given
            name is a wildcard query.If no query text exists,All songs
            matching the name are given
            : docs -- dictionary of selected docs till now
                        returns list of docids in that case
            :onlyA -- means this is the only seletion criteria
        """
        cur = conn.cursor()
        options = self.advOptions
        labels =[]
        label = options["artist"] ## name start with
        if label !='':
            labels =["$"+label]
        label = options["artistend"] ## name ends with
        if label !='':
            labels.append(label+"$")
        if onlyA == True: ## no query text exists
            labeldocs = []
            for label in labels:
                cur.execute("SELECT docid FROM permArtist where key = ? ",(label,))
                row = cur.fetchall()
                if(len(row)<1):
                    return
                pickled = row[0][0]
                docids = pickle.loads(pickled)
                labeldocs.append(docids)
            if len(labels) == 1:
                return labeldocs[0]
            else :
                return intersection(labeldocs[0],labeldocs[1])
        elif len(docs) > 0:
            seldocids = list(docs.keys())
            labeldocs = []
            for label in labels:
                cur.execute("SELECT docid FROM permArtist where key = ? ",(label,))
                row = cur.fetchall()
                if(len(row)<1):
                    return
                pickled = row[0][0]
                docids = pickle.loads(pickled)
                labeldocs.append(docids)
            if len(labels) == 1:
                docids= labeldocs[0]
            else:
                docids= intersection(labeldocs[0],labeldocs[1])
            for id in seldocids: ## filtering on artist
                if id not in docids:
                    del docs[id]

    def filterByYear(self,conn,docs=[],onlyyear = False):
        """filters song documents based on the details of year given
            .If no query text exists,All songs matching the name are given
            : docs -- dictionary of selected docs till now
            :onlyyear -- means this is the only seletion criteria
                        returns list of docids in that case
            (Year1==year2) -> select for that year
            (Year1, blank) -> include all entries after or in year1
            (blank, year2) -> include all entries before on in year2
            (blank, blank) -> Not processed
        """
        cur = conn.cursor()
        options = self.advOptions
        yfrom = options["from"]
        yto = options["to"]
        if yfrom!='' and yto!='':
            if yfrom == yto:
                condstr = "= ? "
                param=[yfrom]
            else:
                condstr = "Between ? AND ? "
                param = [yfrom,yto]
        else:
            if yfrom !='':
                condstr = ">= ? "
                param =[yfrom]
            else:
                condstr = "<= ? "
                param = [yto]
        if onlyyear == True:  ## no query string
            querystr = "SELECT docid FROM yearDoc where year "+condstr
            cur.execute(querystr,param)
            docids = [item[0] for item in cur.fetchall()]
            return docids
        elif len(docs) > 0:
            docids = list(docs.keys())
            questionmarks = '?' *len(docids)
            querystr = "SELECT docid FROM yearDoc where year "+condstr+"and docid in ({})".format(','.join(questionmarks))
            plist = param + docids
            cur.execute(querystr,plist)
            seldocids = [item[0] for item in cur.fetchall()]
            for id in docids:
                if id not in seldocids:
                    del docs[id]

    def filterByGenre(self,conn,docs,docids=None,onlyg = False):
        """filters song documents based on the genre given
            .If no query text exists,All songs matching the name are given
            : docs -- dictionary of selected docs till now
            :onlyg -- means this is the only seletion criteria,
                     returns list of docids in that case
        """
        cur = conn.cursor()
        options = self.advOptions
        gen = options["genre"].capitalize()
        if onlyg == True:
            cur.execute("SELECT docid FROM genreDoc where genre=? ",(gen,))
            docids = [item[0] for item in cur.fetchall()]
            return docids
        else:
            if len(docs) > 0:
                docids = list(docs.keys())
            if len(docids)==0:
                return
            questionmarks = '?' *(len(docids))
            querystr = "SELECT docid FROM genreDoc WHERE genre=? and docid in ({})".format(','.join(questionmarks))
            plist = [gen] + docids
            cur.execute(querystr,plist)
            seldocids = [item[0] for item in cur.fetchall()]
            for id in docids:
                if id not in seldocids:
                    del docs[id]

    def getAdvResults(self,tokens):
        """Retriving and processing indexes
           based on query criteria
         :tokens - pre processed query tokens
         :returns : dictionary of documents
                    satisfying all query conditons
        """
        proximity = 1   #change this for approximate search
        docs ={}
        docids = []
        conn = create_connection(self.queryEngine.dbfile)
        cur = conn.cursor()
        options = self.advOptions
        docs = self.getIndexes(tokens,options["allterms"],options["pos"]) #term index

        if options["pos"] == 1:  #filtering based on postions
            for doc in list(docs.keys()):
                termdict = docs[doc]
                posList = [] ## postion list of all query terms in doc
                for term in termdict: # remove postions from final dict
                    tlist = termdict[term]
                    unpickled = pickle.loads(tlist[1])
                    unpickled.sort()
                    posList.append(unpickled)
                    termdict[term] = tlist[0]
                refList = posList[0]
                selDoc = False
                for refpos in refList:
                    pp = refpos+proximity # window for the next terms
                    foundflag = False
                    for i in range(1,len(posList)):
                        radius= pp+i
                        for tarpos in posList[i]:
                            foundflag = False
                            selDoc = False
                            if tarpos>refpos and tarpos<radius:
                                foundflag=True
                                selDoc = True
                                break
                        if foundflag == False:
                            break;
                    if foundflag == True:
                        selDoc == True
                        break
                if selDoc == False:
                    del docs[doc]
                else:
                    #if options["allterms"] == 1:
                    if len(posList) < len(tokens):
                        del docs[doc]
        #            print(posList)
        #            print(docs[doc])
        #print(len(docs))

        #based on artist input from user
        if self.queryText == '' and (options["artist"]!='' or options["artist"]!=''):
            docids = self.filterArtist(conn,onlyA = True)
        elif options["artist"]!='' or options["artistend"]!='':
            self.filterArtist(conn,docs = docs)

        #based on name input from user
        if self.queryText == '' and (options["songname"]!=''or options["songend"]!=''):
            docids = self.filterName(conn,onlyN = True)
        elif options["songname"]!='' or options["songend"]!='':
            self.filterName(conn,docs = docs)

        # query based on the year input from user
        if self.queryText == '' and (options["from"]!='' or options["to"]!=''):
            docids = self.filterByYear(conn,onlyyear = True)
        elif options["from"]!='' or options["to"]!='':
            self.filterByYear(conn,docs = docs)

        #query based on the genre input by user
        if self.queryText == '' and options["from"]=='' and options["to"]=='' and options["genre"]!='':
            docids = self.filterByGenre(conn,docs = docs,onlyg = True)
        elif (len(docs)>0 or len(docids)>0 ) and options["genre"]!='':
            self.filterByGenre(conn,docs = docs,docids=docids)
        if (len(docs)==0 and len(docids)>0 ):
            return docids

        return docs

    def advQueryProcessing(self,engine):
        """Processing based on self.advOptions values
            options is a dictionary of following terms
            "allterms"
            "songname"
            "songend"
            "artist",
            "artistend"
            "genre"
            "pos"
            "from"
            "to"
            Arguments:
                engine -- object to which the Query object belongs
        """
        print("******Advanced query processing******")
        starttime = datetime.datetime.now()
        print("Start time",str(starttime))
        print("Query---",self.queryText)

        self.queryEngine = engine
        q_tokens = tokenize(self.queryText) #tokenize queryText
        qs_tokens,qs_dict = stem(q_tokens)
        #    if len(qs_tokens) == 0:   ## uncomment to disallow blank query text
                #engine.noResult = True
                #return

        # all the documents satisfying the criteria
        querydocs = self.getAdvResults(qs_tokens)

        #Ranking based on score
        songHeap = []
        for doc in querydocs:
            if(type(querydocs)==type([])): # case where score is not available
                song = selSong(doc,{})
            else:
                song = selSong(doc,querydocs[doc]) # calculates score document at a time
            songHeap.append(song)
        if len(songHeap)==0:
            #engine.noResult = True
            self.noResult = True
            printDuration(starttime)
            return
        self.queryResult = songHeap
        songHeap.sort(reverse=True)

        #Fetching song details
        count = engine.displayLength
        self.nextSongListPrep(0,count)

        # retrieval time
        printDuration(starttime)
