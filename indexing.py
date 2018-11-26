""" Builds/updates all the indexes for the search SearchEngine
    DB FILE --- engine.db
    Build Option:
        Creates the following sqlite db tables
        - songs(id,name ,year ,artist ,genre ,lyrics)
        - terms(term,cfreq ,dfreq)
        - termdoc(term ,docid , tfreq ,dscore ,posList)
        - permArtist(key ,docid )
        - permName(key,docid )
        - genreDoc(genre ,docid)
        - yearDoc(year ,docid )
    Update Option:
        -updates the new dataset and it's indexes into the above tables
"""
import sqlite3
import csv
import os
import pickle
import math
from preprocessing import tokenize,stem
import datetime

#numFiles = None
dbname = "engine.db"

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    Arguments:
        db_file -- database file
    return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        #print("connect suceess")
        return conn
    except Error as e:
        print(e)
    return None

def load_songs(filename):
    """One Time activity done during configuration
       -Loads the dataset into sql lite db - engine.db
       -creates table SONGS and loads dataset
       Arguments:
        filename -- CSV file containing the dataset
    """
    if os.path.exists(dbname):
        os.remove(dbname)

    conn = create_connection(dbname)
    cur=conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY,
                name TEXT,year Integer,artist TEXT,genre TEXT,lyrics Text)""") #indexes to a line number in file
    cur_id = 0
    with open(filename,"r",encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        header =next(csvreader)
        for row in csvreader:
            cur_id = cur_id+1
            row[0] = cur_id
            sql_q = "INSERT INTO songs VALUES(?,?,?,?,?,?)"
            cur.execute(sql_q,row)
            if cur_id == 20000:
                break
    conn.commit()
    conn.close()

def update_song_db():
    print("")

def updateTermTable(id,termslocal,conn):
    """updates the document statistics in tables <term> and <termdoc>
        Arguments:
            id -- id of the song
            termslocal -- document level statistics of the songs
            conn -- current db connection handle
    """
    cur = conn.cursor()
    for key in termslocal:
        if any(char.isdigit() for char in key):
            continue
        cur.execute("SELECT * FROM terms WHERE term=?",(key,))
        row = cur.fetchall()
        if len(row)>1:
            print("multiple terms greater than 1")
        posList = termslocal[key][1]  #position list
        pickleDump = pickle.dumps(posList,protocol=pickle.HIGHEST_PROTOCOL)
        if(len(row)==0): #insert
            newrow = [key,termslocal[key][0],1]
            cur.execute("INSERT into terms(term,cfreq,dfreq) values(?,?,?)",newrow)
        else:           #update
            df = row[0][2] +1
            cf = row[0][1]+termslocal[key][0]
            valList = [cf,df,key]
            cur.execute("UPDATE terms SET cfreq =?,dfreq = ? where term = ?",valList)
        upList =[key,id,termslocal[key][0],pickleDump]
        cur.execute("INSERT or IGNORE into termdoc(term,docid,tfreq,posList) values(?,?,?,?)",upList)

def updateGenreYear(gen,yr,id,conn):
    """Update into db table genreDoc & yearDoc
       Arguments:
        gen - genre of the cur song
        yr - year
        if - unique song id
        conn - curent db connection
    """
    cur = conn.cursor()
    cur.execute("INSERT into genreDoc values(?,?)",[gen,id])
    cur.execute("INSERT into yearDoc values(?,?)",[yr,id])

def getPermutermKeys(label):
    """for a given label generates all permuterm rotations
        and divides the key label into two parts
         ex: lo$hel -> key1 = $hel , key2 = lo$
        Arguments:
            label -- label to generate index from
        return:
         dictionary of all keys
    """
    label = label
    keys = {}
    l_length = len(label)
    for i in range(1,l_length):
        key1 = label[-i:]+"$"
        key2 = "$"+label[:-i]
        keys[key1] = None
        keys[key2] = None
    return keys

def permuterm(label,docid,conn,tablename):
    """Update into db table permterm indexes
       Arguments:
       label - index, key of the table
       dcoid - to append to the correspondin label entry
        tablename - the name of the table
        conn - curent db connection
    """
    keys = getPermutermKeys(label)
    cur = conn.cursor()
    for key in keys:
        qstr = "SELECT * FROM "+tablename+" WHERE key=?"
        cur.execute(qstr,(key,))
        row = cur.fetchall()
        if len(row)>0:
            pickled = row[0][1]
            unpickled = pickle.loads(pickled)
            unpickled.append(docid)
            pickleDump = pickle.dumps(unpickled,protocol=pickle.HIGHEST_PROTOCOL)
            qstr = "UPDATE "+tablename+" SET docid = ? where key = ?"
            cur.execute(qstr,[pickleDump,key])
        else:
            pickleDump = pickle.dumps([docid],protocol=pickle.HIGHEST_PROTOCOL)
            qstr = "INSERT into " +tablename+" values(?,?)"
            cur.execute(qstr,[key,pickleDump])

def calculate_Tf_Idf(termscur,conn):
    """update tf-idf score for all entries in termdoc table
       Arguments:
        termscur -- cursor
        conn -- current db connection
    """
    termscur.execute("SELECT count() FROM songs")
    numFiles = termscur.fetchall()[0][0]
    termscur.execute('SELECT * FROM terms')
    for row in termscur:
        tdcur = conn.cursor()
        tdcur.execute('SELECT * FROM termdoc where term = ?',(row[0],))
        for td in tdcur:
            tfidfscore = td[2]* math.log((numFiles/row[2]),10)    #tf*idf
            upcur = conn.cursor()
            upcur.execute("UPDATE termdoc SET dscore=? where term = ? AND docid=?",[tfidfscore,td[0],td[1]])

def build_indexes():
    """Indexing the documents and updating into db"""

    print("Building all indexes ")
    conn = create_connection(dbname)
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS terms(term TEXT PRIMARY KEY,cfreq INTEGER,dfreq INTEGER)")
    cur.execute("""CREATE TABLE IF NOT EXISTS termdoc(term INTEGER,docid INTEGER,
                    tfreq INTEGER,dscore REAL,posList TEXT,
                    FOREIGN KEY (term)REFERENCES terms(term),
                    FOREIGN KEY (docid)REFERENCES songs(id),
                    PRIMARY KEY (term, docid))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS permArtist(key Text,docid Text,
                    FOREIGN KEY (docid)REFERENCES songs(id),
                    PRIMARY KEY (key))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS permName(key Text,docid Text,
                    FOREIGN KEY (docid)REFERENCES songs(id),
                    PRIMARY KEY (key))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS genreDoc(genre Text,docid INTEGER,
                    FOREIGN KEY (docid)REFERENCES songs(id),
                    PRIMARY KEY (genre, docid))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS yearDoc(year Text,docid INTEGER,
                    FOREIGN KEY (docid)REFERENCES songs(id),
                    PRIMARY KEY (year, docid))""")
    cur.execute('SELECT * FROM songs')
    for row in cur:
        tokens = tokenize(row[5])
        if not tokens:
            continue
        stem_tokens ,term_dict_local= stem(tokens)         #PorterStemmer
        updateTermTable(row[0],term_dict_local,conn)
        updateGenreYear(row[4],row[2],row[0],conn)
        permuterm(row[3],row[0],conn,"permArtist") # perm artist
        permuterm(row[1],row[0],conn,"permName") #Name
    print("calculating tfidf")
    calculate_Tf_Idf(cur,conn)
    now = datetime.datetime.now()
    print(str(now))
    conn.commit()
    conn.close()

    now = datetime.datetime.now()
    print(str(now))

def rebuild_indexes():
    print("")

if  __name__ == '__main__':
    print("Choose one of the following options:")
    print("1.Rebuilt all indexes from scratch")
    print("2.Add new song documents to the dataset")
    userInp = int(input())
    if userInp == 1:
        now = datetime.datetime.now()
        print(str(now))
        load_songs("lyrics.csv")
        build_indexes()
    elif userInp == 2:
        newdatsetfile = input("Enter file name in current path")
        update_song_db(newdatsetfile)
        rebuild_indexes()
