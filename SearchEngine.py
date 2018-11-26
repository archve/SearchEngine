""" 
    Dataset used : kaggle data set of 380000+ songs from metrolyrics
        https://www.kaggle.com/gyani95/380000-lyrics-from-metrolyrics/home

"""
from tkinter import Tk,Button,Entry,StringVar,Label,PhotoImage,Frame,Scrollbar,Canvas,IntVar,Checkbutton
from query import Query
from PIL import ImageTk, Image

class SearchEngine:
    """
        All the method to render the UI of the application and
        their callback handlers to process the input
    """

    def __init__(self):
        """All paramters of the engine and loading homepage"""
        self.terms ={}       #not needed now    #This can be changed to have different types of indeces of indexes class
        self.songs = {}     #not needed
        self.dbfile = "engine.db"
        self.currentQuery = None
        self.bgImage = None
        self.currentFrame = None
        self.window = None
        self.topSearch = None
        self.advancedSearch = None
        self.displayLength = 10
        #self.indexPrompt()
        self.homepage()

    def searchButtonCallBack(self,qsobj,window):
        """Called from <search> Button
           Arguments:
           qsobj  -- object of the query text box
           window -- current window <not needed remove this from logic>
        """
        qr = Query(qsobj.get())
        self.currentQuery = qr
        self.topSearch = False  #disabling lucky search
        qr.queryProcessing(self) # updates self.curretQuery.queryResult
        self.displayOutput()

    def luckySearchBtnCallBack(self,qsobj,window):
        """Called from <luckysearch> Button
           Arguments:
           qsobj  -- object of the query text box
           window -- current window <not needed remove this from logic>
        """
        qr = Query(qsobj.get())
        self.currentQuery = qr
        self.topSearch = True
        qr.queryProcessing(self)
        self.displayOutput()

    def advSearchCallBack(self,options):
        """Called from <search> Button on advanced search page
           Arguments:
           options  -- serach criteria
        """
        self.currentQuery.queryText = options["query"].get()
        for key in options:
            print(key,options[key].get())
            self.currentQuery.advOptions[key] = options[key].get()
        self.currentQuery.advQueryProcessing(self)
        self.displayOutput()

    def advSearchFrame(self):
        """Building advanced search frame
        """
        self.currentFrame.destroy()

        asFrame = Frame(self.window)
        asFrame.grid(row=0,column=0)
        self.currentFrame = asFrame

        headingFrame = Frame(asFrame)
        headingFrame.grid(row=0,column=0,pady=25)
        headingLabel = Label(headingFrame,text="Advanced Search Options",borderwidth=3,relief="raised",
                        underline=True,fg="black",font="Verdana 16 bold ")
        headingLabel.grid(row = 0, column = 0)

        advOptionsFrame =  Frame(asFrame)
        #self.currentFrame = advOptionsFrame
        advOptionsFrame.grid(row=1,column=0)

        queryLabel = Label(advOptionsFrame,text="Query",fg="black",font="Helvetica 12 ")
        queryLabel.grid(row = 0, column = 0,sticky="w")
        queryStrObj = StringVar()
        queryTextbox = Entry(advOptionsFrame,textvariable = queryStrObj,fg="black",font="Helvetica 12 ")
        queryTextbox.insert(0, self.currentQuery.queryText)
        queryTextbox.grid(row=0,column = 1,sticky="w")

        chkVar1 = IntVar()
        Checkbutton(advOptionsFrame, text="Result should contain all Query Terms", variable=chkVar1,
                    fg="black",font="Helvetica 12 ").grid(row=1,column=0, sticky="w")
        chkVar2 = IntVar()
        Checkbutton(advOptionsFrame, text="Exact Match/maintain order", variable=chkVar2,
                fg="black",font="Helvetica 12 ").grid(row=1,column=1,sticky="w")

        songNameLabel = Label(advOptionsFrame,text="Song Name Start",fg="black",font="Helvetica 12 ")
        songNameLabel.grid(row = 2, column = 0,sticky="w")
        songNameObj = StringVar()
        songNameTextBox = Entry(advOptionsFrame,textvariable = songNameObj)
        songNameTextBox.grid(row=2,column = 1,sticky="w")
        songNameEndLabel = Label(advOptionsFrame,text="End",fg="black",font="Helvetica 12 ")
        songNameEndLabel.grid(row = 2, column = 2,sticky="w")
        songNameEndObj = StringVar()
        songNameEndTextBox = Entry(advOptionsFrame,textvariable = songNameEndObj)
        songNameEndTextBox.grid(row=2,column = 3,sticky="w")

        artistNameLabel = Label(advOptionsFrame,text="Artist First",fg="black",font="Helvetica 12 ")
        artistNameLabel.grid(row = 3, column = 0,sticky="w")
        artistNameObj = StringVar()
        artistNameTextBox = Entry(advOptionsFrame,textvariable = artistNameObj)
        artistNameTextBox.grid(row=3,column = 1,sticky="w")
        artistNameEndLabel = Label(advOptionsFrame,text="Artist Last",fg="black",font="Helvetica 12 ")
        artistNameEndLabel.grid(row = 3, column = 2,sticky="w")
        artistNameEndObj = StringVar()
        artistNameEndTextBox = Entry(advOptionsFrame,textvariable = artistNameEndObj)
        artistNameEndTextBox.grid(row=3,column = 3,sticky="w")

        genreLabel = Label(advOptionsFrame,text="Genre",fg="black",font="Helvetica 12 ")
        genreLabel.grid(row = 4, column = 0,sticky="w")
        genreObj = StringVar()
        genreTextBox = Entry(advOptionsFrame,textvariable = genreObj)
        genreTextBox.grid(row=4,column = 1,sticky="w")

        yearStartLabel = Label(advOptionsFrame,text="Year From",fg="black",font="Helvetica 12 ")
        yearStartLabel.grid(row = 5, column = 0,sticky="w")
        yearStartObj = StringVar()
        yearStartTextBox = Entry(advOptionsFrame,textvariable = yearStartObj)
        yearStartTextBox.grid(row=5,column = 1,sticky="w")
        yearEndLabel = Label(advOptionsFrame,text="To",fg="black",font="Helvetica 12 ")
        yearEndLabel.grid(row = 5, column = 2,sticky="w")
        yearEndObj = StringVar()
        yearEndTextBox = Entry(advOptionsFrame,textvariable = yearEndObj)
        yearEndTextBox.grid(row=5,column = 3,sticky="w")
        options = {"query":queryStrObj,"allterms":chkVar1,
                    "songname":songNameObj,"songend":songNameEndObj,
                    "artist":artistNameObj,"artistend":artistNameEndObj,"genre":genreObj,
                    "pos":chkVar2,"from":yearStartObj,"to":yearEndObj}
        searchButton = Button(advOptionsFrame,text = "Search",fg="black",font="Helvetica 12 ",
                    command= lambda : self.advSearchCallBack(options))
        searchButton.grid(row=6,column = 0)

    def advSearchBtnCallBack(self,qsobj,window):
        """Called from <search> Button on home page
           Arguments:
           qsobj  -- object of the query text box
           window -- current window <not needed remove this from logic>
        """
        qr = Query(qsobj.get())
        self.currentQuery = qr
        self.topSearch = False
        self.currentQuery.topSearch = False
        self.currentQuery.advSearch = True
        self.advSearchFrame()
        #qr.queryProcessing(self)
        #self.displayOutput()

    def onClosing(self):
        exit()

    def songDetailsFrame(self,subFrame,songObj):
        """Frame displaying song song song details
            Argumets:
                subframe - parent Frame
                song Obj - reference to the song
        """
        curRow =0
        curCol =0
        """canvas=Canvas(subFrame,bg='#FFFFFF',width=300,height=300,scrollregion=(0,0,500,500))
        vbar=Scrollbar(subFrame,orient=VERTICAL)
        vbar.pack(side=RIGHT,fill=Y)
        vbar.config(command=canvas.yview)
        canvas.config(width=300,height=300)
        canvas.config(yscrollcommand=vbar.set)
        canvas.pack(side=LEFT,expand=True,fill=BOTH)"""
        for key in songObj.songdetails:
            headText = key
            headLabel = Label(subFrame,text=headText.capitalize(),fg="red",font="Verdana 14 bold",underline =True)
            headLabel.grid(row = curRow, column = curCol)
            curRow = curRow+1
            contentText = songObj.songdetails[key]
            contentLabel = Label(subFrame,text=contentText,fg="dark green",font="Helvetica 12 italic")
            contentLabel.grid(row = curRow, column = curCol)
            curRow = curRow+1

    def songLinkCallback(self,subFrame,widgetDict,curFrame,event=None):
        """ song name HyperLink on results page
        """
        curFrame.destroy()
        caller = event.widget
        self.songDetailsFrame(subFrame,widgetDict[caller])

    def songListFrame(self,subFrame,count):
        """Frame for displaying list of songs
        """
        curRow =0
        curCol =0
        maxEntries = self.displayLength
        displayCount = count
        colOutputFrame = Frame(subFrame)
        endOfResultFlag = False
        colOutputFrame.grid(row=0,column=0)
        widgetDict = {}
        headTexts =["Sl#","Song","Year","Artist","Genre","Score"]
        for i in range(len(headTexts)):
            headLabel = Label(colOutputFrame,text=headTexts[i],fg="red",font="Verdana 14 bold")
            headLabel.grid(row = curRow, column = curCol,sticky = "w")
            curCol = curCol+1
        curRow = curRow+1
        for idx in range(count,count+maxEntries):
            if idx < len(self.currentQuery.queryResult) and idx>=0:
                songObj =self.currentQuery.queryResult[idx]
                curCol=0
                displayCount = displayCount+1
                contentText = displayCount
                contentLabel = Label(colOutputFrame,text=contentText,
                                fg="dark green",font="Helvetica 12 italic")
                contentLabel.grid(row = curRow, column = curCol,sticky="w")
                curCol = curCol+1
                for key in songObj.songdetails:
                    if key=="lyrics":
                        continue
                    contentText = songObj.songdetails[key]
                    if key == "name": #Create L=HyperLink to song page
                        contentLabel = Label(colOutputFrame, text=contentText,
                            fg="green", font="Helvetica 12 italic",cursor="hand2")
                        contentLabel.bind("<Button-1>", lambda event:
                            self.songLinkCallback(event=event,subFrame=subFrame,
                            widgetDict=widgetDict,curFrame=colOutputFrame))
                        widgetDict[contentLabel] = songObj
                    else:
                        contentLabel = Label(colOutputFrame,text=contentText,
                                    fg="dark green",font="Helvetica 12 italic")
                    contentLabel.grid(row = curRow, column = curCol,sticky="w")
                    curCol = curCol+1
                contentText = songObj.score
                contentLabel = Label(colOutputFrame,text=contentText,
                                fg="dark green",font="Helvetica 12 italic")
                contentLabel.grid(row = curRow, column = curCol,sticky="w")
                curCol = curCol+1
                curRow = curRow+1
            else:
                contentLabel = Label(colOutputFrame,text="END OF RESULTS",
                                fg="red",font="Helvetica 12 italic")
                contentLabel.grid(row = curRow, column = 0,columnspan = 4)
                curRow = curRow+1
                endOfResultFlag = True
                break
        if endOfResultFlag==False:
            nextButton = Button(colOutputFrame,text = "Next",command= lambda :
                                self.nextButtonCallBack(subFrame,displayCount,colOutputFrame))
            nextButton.grid(row=curRow,column=1,sticky = "w")
        if count>=maxEntries:
            prevButton =Button(colOutputFrame,text = "Previous",command= lambda :
                                self.prevButtonCallBack(subFrame,count,displayCount,colOutputFrame))
            prevButton.grid(row=curRow,column=0,sticky = "w")

        curRow = curRow+1
        bottomText ="Total Number of Search Results = "+str(len(self.currentQuery.queryResult))
        BottomLabel = Label(colOutputFrame,text=bottomText,fg="light green",font="Verdana 14 bold")
        BottomLabel.grid(row = curRow, column = 0,columnspan=4,sticky="w")

    def nextButtonCallBack(self,subFrame,start,curFrame):
        curFrame.destroy()
        self.currentQuery.nextSongListPrep(start,start+self.displayLength)
        self.songListFrame(subFrame,start)

    def prevButtonCallBack(self,subFrame,prevcount,count,curFrame):
        curFrame.destroy()
        count = count -self.displayLength-(count-prevcount)
        self.songListFrame(subFrame,count)

    def Home_Frame(self,window):
        """ on home page
        """
        homeFrame = Frame(window)
        homeFrame.grid(row=0,column=0)
        self.currentFrame = homeFrame

        imgFrame = Frame(homeFrame)
        imgFrame.grid(row=0,column=0)
        self.bgImage = ImageTk.PhotoImage(Image.open("LyricsSearch.jpg"))  # PIL solution
        labelPhoto = Label(imgFrame,image = self.bgImage)
        labelPhoto.grid(row=0,column=0)

        txtFrame=Frame(homeFrame)
        txtFrame.grid(row=1,column=0)
        queryStrObj = StringVar()
        queryTextbox = Entry(txtFrame,textvariable = queryStrObj,fg="black",font="Verdana 12")
        queryTextbox.grid(row=0,column = 0,columnspan=3)

        btnFrame=Frame(homeFrame)
        btnFrame.grid(row=2,column=0)
        searchButton = Button(btnFrame,text = "Search",fg="black",font="Verdana 8 bold ",command= lambda :
                                self.searchButtonCallBack(queryStrObj,window))
        topResultButton =  Button(btnFrame,text = "Lucky Search",fg="black",font="Verdana 8 bold ",command= lambda :
                                self.luckySearchBtnCallBack(queryStrObj,window))
        advSearchBtn =Button(btnFrame,text = "Advanced Search",fg="black",font="Verdana 8 bold ",command= lambda :
                                self.advSearchBtnCallBack(queryStrObj,window))
        searchButton.grid(row=0,column = 0)
        topResultButton.grid(row=0,column = 1)
        advSearchBtn.grid(row=0,column=2)

    def resultPageSearchBoxFrame(self,parent):
        searchBoxFrame = Frame(parent,borderwidth=3,relief="sunken")
        searchBoxFrame.grid(row=0,column=0,sticky="w")
        queryStrObj = StringVar()
        queryTextbox = Entry(searchBoxFrame,textvariable = queryStrObj,fg="black",font="Helvetica 12 ")
        queryTextbox.insert(0, self.currentQuery.queryText)
        queryTextbox.grid(row=0,column = 0,sticky="w")
        searchButton = Button(searchBoxFrame,text = "Search",fg="black",font="Helvetica 12 ",
                    command= lambda : self.searchButtonCallBack(queryStrObj,self.window))
        topResultButton =  Button(searchBoxFrame,text = "Lucky Search",fg="black",font="Helvetica 12",
                    command= lambda : self.luckySearchBtnCallBack(queryStrObj,self.window))
        advSearchBtn =Button(searchBoxFrame,text = "Advanced Search",fg="black",font="Helvetica 12",
                    command= lambda : self.advSearchBtnCallBack(queryStrObj,self.window))
        searchButton.grid(row=0,column = 1)
        topResultButton.grid(row=0,column = 2)
        advSearchBtn.grid(row=0,column=3)

    def Result_Frame(self):
        self.currentFrame.destroy()

        resultFrame = Frame(self.window)
        self.currentFrame = resultFrame
        resultFrame.grid(row=0,column=0)
        self.resultPageSearchBoxFrame(resultFrame)
        outputFrame =  Frame(resultFrame)
        outputFrame.grid(row=1,column=0)
        if(self.topSearch):
            self.songDetailsFrame(outputFrame,self.currentQuery.queryResult[0])
        else:
            self.songListFrame(outputFrame,0)

    def homepage(self):
        window = Tk()
        self.window = window
        window.title("Find That Song")
        window.update_idletasks()
        #scrollbar = Scrollbar(window,orient="vertical")
        #scrollbar.grid( row=3,column=1,sticky ="nsew")
        width = 700
        height = 500
        x = (window.winfo_screenwidth()//2) - (width//2)
        y = (window.winfo_screenheight()//2)-(height//2)
        window.geometry('{}x{}+{}+{}'.format(width,height,x,y))
        window.iconbitmap("licon.ico")
        self.Home_Frame(self.window)
        window.protocol("WM_DELETE_WINDOW", self.onClosing)
        window.mainloop()

    def recmpButtonCallback(self,w):
        firstSteps(self)
        w.destroy()

    def no_recmpButtonCallback(self,w):
        loadIndexes()
        w.destroy()

    def indexPrompt(self):
        window= Tk()
        window.title("Verify Recompute")
        heading=Label(window,text="""Do you want to recompute the indexes and
                                    preprocess the Dataset again?""")
        heading.grid(row=0,column=1)
        recmp = Button(window,text='Recompute indexes', command=lambda:
                                            self.recmpButtonCallback(window))
        recmp.grid(row = 2,column=2)
        no_recmp=Button(window,text='No, use computed indexes', command=lambda:
                                            self.no_recmpButtonCallback(window))
        no_recmp.grid(row = 2,column=1)
        window.protocol("WM_DELETE_WINDOW", self.onClosing)
        window.mainloop()

    def displayOutput(self):
        self.Result_Frame()

if __name__ == '__main__':
    engine = SearchEngine()
