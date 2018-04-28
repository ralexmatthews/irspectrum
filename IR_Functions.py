"""
Program: IRSpectrum.py
Programmed by: Josh Ellis, Josh Hollingsworth, Aaron Kruger, Alex Matthews, and
    Joseph Sneddon
Description: This program will recieve an IR Spectrograph of an unknown
    molecule and use our algorithm to compare that graph to a stored database of
    known molecules and their IR Spectrographs. This program will then return a
    list of the closest Spectrographs matches as determined by our algorithm.
IR_Functions.py: This part of the program contains most of the functions used by
    Query.py and UpdatedDB.py.
"""
#---------------------------------Imports--------------------------------------
import PyPDF2
import sqlite3
from PIL import Image
import sys
import warnings
import os

warnings.filterwarnings("ignore")
#------------------------------------------------------------------------------

#---------------------------------Variables------------------------------------

#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------
def PullImages(filename):
    '''
    Pull graph image from first page of PDF
    '''
    file = PyPDF2.PdfFileReader(open(filename, "rb"))
    xObject = file.getPage(0)


    xObject = xObject['/Resources']['/XObject'].getObject()

    images=[]

    for obj in xObject:

        if xObject[obj]['/Subtype'] == '/Image':
            size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
            data = xObject[obj]._data
            if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                mode = "RGB"
            else:
                mode = "P"

            if xObject[obj]['/Filter'] == '/FlateDecode':
                img = Image.frombytes(mode, size, data)
                img.save(filename + ".png")
                images+=[filename + ".png"]
            elif xObject[obj]['/Filter'] == '/DCTDecode':
                img = open(filename + ".jpg", "wb")
                img.write(data)
                img.close()
                images+=[filename + ".jpg"]
            elif xObject[obj]['/Filter'] == '/JPXDecode':
                img = open(filename + ".jp2", "wb")
                img.write(data)
                img.close()
                images+=[filename + ".jp2"]
    return images

def PullStructure(filename):
    '''
    Pulls the image of the molecular structure from page 2 as a png
    '''
    file = PyPDF2.PdfFileReader(open(filename, "rb"))
    xObject = file.getPage(1)


    xObject = xObject['/Resources']['/XObject'].getObject()

    images=[]

    for obj in xObject:
        if xObject[obj]['/Subtype'] == '/Image':
            size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
            data = xObject[obj].getData()
            if xObject[obj]['/Filter'] == '/FlateDecode':
                img = Image.frombytes("P", size, data)
                img.save(filename.split('.')[0] + ".png")
                images+=[filename.split('.')[0] + ".png"]
    return images

def PullText(filename):
    '''
    Pull text from the first page of a PDF
    returns an array containing:
    [ SpectrumID, CAS Number, Molecular Formula, Compound Name ]
    '''
    specID = ""
    cas = ""
    formula = ""
    name = ""

    try:
        file = PyPDF2.PdfFileReader(open(filename, "rb"))
        page = file.getPage(0)

        page_content = page.extractText()

        idIndex = page_content.find("Spectrum ID")
        casIndex = page_content.find("CAS Registry Number")
        formulaIndex = page_content.find("Formula")
        nameIndex = page_content.find("CAS Index Name")
        sourceIndex = page_content.find("Source")
        startIndex = casIndex

        begin = idIndex + 11
        end = casIndex
        while begin != end:
            specID += page_content[begin]
            begin += 1

        begin = casIndex + 19
        end = formulaIndex
        while begin != end:
            cas += page_content[begin]
            begin += 1

        begin = formulaIndex + 7
        end = nameIndex
        while begin != end:
            formula += page_content[begin]
            begin += 1

        begin = nameIndex + 14
        end = sourceIndex
        while begin != end:
            name += page_content[begin]
            begin += 1
    except:
        print("There was an error extracting text from the PDF")

    #return [specID, cas, formula, name]
    return {"spectrumID":specID, "cas":cas, "formula":formula, "name":name}

def CleanStructure(filename):
    img = Image.open(filename)
    imgdata=list(img.getdata())#the pixels from the image

    img = Image.new('RGBA', (img.size[0],img.size[1]))

    imgdata=[(i,i,i,255)  if i<31 else (i,i,i,0) for i in imgdata]

    img.putdata(imgdata)
    img.save(filename)

class ReadGraph:
    def __new__(self, image):
        self.image = image
        self.xMin=200
        self.xMax=4100
        self.xRange=self.xMax-self.xMin #the x-range of the graph.
        self.yMin=1.02
        self.yMax=-0.05
        self.yRange=self.yMax-self.yMin #the y-range of the graph.
        #This is the width and height standard for all IR samples
        self.width=1024
        self.height=768
        #the area of each image that we want (the graph)
        self.targetRect=(113,978,29,724) #(left,right,top,bottom)

        return self.readGraph(self)

    #copies pixels from the source image within the targetRect
    def cropRect(self, source):
        left,right,top,bottom=self.targetRect
        newImg=[]
        for y in range(top,bottom+1):
            for x in range(left,right+1):
                newImg+=[source[y*self.width+x]]
        return newImg

    #checks if the pixel at x,y is black
    def pix(self, graph,x,y):
        r,g,b=graph[y*self.width+x]
        if r+g+b>=100:
            return False#not black
        else:
            return True#black

    #These two functions convert graph x,y into scientific x,y
    def convertx(self, x):
        return self.xMin+self.xRange*(x/self.width)
    def converty(self, y):
        return self.yMin+self.yRange*(y/self.height)

    def convertGraph(self, graph):
        """
        Creates a graphData list by finding each black pixel on the x axis. For each
        x get the y range over which the graph has black pixels or None if the graph
        is empty at that x value. It stores the min and max y values in the
        graphData list. Then returns the filled graphData List.
        """
        graphData=[]#to be filled with values from graph
        #For each x get the y range over which the graph has black pixels
        # or None if the graph is empty at that x value
        for x in range(0,self.width):
            graphData+=[None]
            foundPix=False#have you found a pixel while looping through the column
            for y in range(0,self.height):
                p=self.pix(self,graph,x,y)#is the pixel black
                if p and not foundPix:
                    #record the first black pixels y value
                    foundPix=True
                    maxVal=y
                elif not p and foundPix:
                    #record the last black pixels y value
                    minVal=y
                    graphData[-1]=(minVal,maxVal)#write these values to data
                    break#next x

        return graphData

    #convert graph into datapoints
    def cleanData(self, graphData):
        data=[]
        for x in range(len(graphData)):
            #Points in format x,y
            if graphData[x]:
                data+=[(self.convertx(self,x),self.converty(self,graphData[x][1]))]

        return data

    def readGraph(self,):
        #Crops the image
        img = Image.open(self.image)
        imgdata=list(img.getdata())#the pixels from the image

        #The graph is cut out of the larger image
        graph=self.cropRect(self,imgdata)

        #width and height of out cropped graph
        self.width=self.targetRect[1]-self.targetRect[0]+1
        self.height=self.targetRect[3]-self.targetRect[2]+1

        #Fills graphData with values from 'graph'
        graphData = self.convertGraph(self,graph)

        #final value written to file
        data = self.cleanData(self,graphData)
        return data

def ConvertQuery(l,tTypes):
    queryDict={}
    for tType in tTypes:
        queryDict[tType]=[]
        queryDict[tType]+=Convert(l,tType)
    return queryDict

class Convert():
    def __new__(self,l,tType):
        if "raw" == tType:
            return l
        else:
            if tType.split('.')[0] == "Cumulative":
                return self.Cumulative(self,l,int(tType.split('.')[-1]))
            elif tType.split('.')[0] == "CumulativePeak":
                return self.CumulativePeak(self,l,int(tType.split('.')[-1]))
            elif tType.split('.')[0] == "AbsoluteROC":
                return self.AbsoluteROC(self,l,int(tType.split('.')[-1]))
        raise ValueError("Convert type not found: "+str(tType))

    def Cumulative(self,l,scanrange):
        l=['x']+l[:]+['x']
        divisor=0
        total=0
        for i in range(1,scanrange+1):
            divisor+=max(0.1,l[i][1])
        retlist=[]
        for i in range(1,len(l)-1):

            low=max(0,i-scanrange)
            high=min(len(l)-1,i+scanrange)

            total-=max(0.1,l[low][1]) if l[low]!="x" else 0
            total+=max(0.1,l[i][1]) if l[i]!="x" else 0

            divisor-=max(0.1,l[low][1]) if l[low]!="x" else 0
            divisor+=max(0.1,l[high][1]) if l[high]!="x" else 0

            retlist+=[(l[i][0],total/divisor)]

        return retlist

    def CumulativePeak(self,l,scanrange):#peak to peak transformation
        '''
        Find all peaks in list l
        Weight peaks by their height and how far they are from other taller peaks
        '''
        retlist=[]
        lenl=len(l)
        for i in range(lenl):

            #current x and y values for point i in list l
            curx=l[i][0]
            cury=l[i][1]

            #If this point has the same y value as the previous point
            # then continue to the next point
            if i-1>=0: # and i+1<lenl
                if (l[i-1][1] == cury):
                    retlist+=[(curx,0)]
                    continue

            #Search right of the point until you run into another peak or off the graph
            # sum the difference between cury and the graph at i+j to find the area right of the peak

            s1=0
            j=1
            while i+j<lenl and l[i+j][1] <= cury and j<scanrange:
                s1+= (cury - l[i+j][1]) * (l[i+j][0]-l[i+j-1][0])
                j+=1

            #Same opperation but searching left
            s2=0
            j=-1
            while i+j>=0 and l[i+j][1] <= cury and j>-scanrange:
                s2+= (cury - l[i+j][1]) * (l[i+j+1][0]-l[i+j][0])
                j-=1

            #take the lowest of the 2 values
            retlist+=[(curx,min(s1,s2)*cury)]

        return self.Cumulative(self,retlist,scanrange)

    def AbsoluteROC(self,l,scanrange):
        '''
        The absolute value of the slope of the curve in list l
        Note: this method may not be useful for matching compounds
        '''
        retlist=[]
        for i in range(len(l)-1):
            retlist+=[(l[i][0], abs(l[i+1][1]-l[i][1]) )]

        return self.Cumulative(self,retlist,scanrange)

class Compare():
    def __new__(self,tType,subject,query):
        if not "raw" in tType or "raw" == tType:
            return self.directCompare(self,subject,query)
        else:
            if tType.split('.')[0] in ["Cumulative","CumulativePeak","AbsoluteROC"]:
                return self.directCompare(self, Convert(subject,tType) ,query)
        raise ValueError("Compare type not found: "+str(tType))

    def directCompare(self,transformation1,transformation2):
        dif=0
        #Swap if needed, want t1 to be sorter than t2
        if len(transformation1)>len(transformation2):
            tmp=transformation1[:]
            transformation1=transformation2[:]
            transformation2=tmp

        k=0
        for j in range(len(transformation1)):
            while transformation1[j][0]>transformation2[k][0] and k<len(transformation2)-1:
                k+=1
            dif+=abs(transformation1[j][1]-transformation2[k][1])

        return dif

def AddSortResults(difDict,casNums):
    tranformTypes=list(difDict.keys())[:]

    difList=[]
    for i in range(len(casNums)):
        dif=0
        for trform in tranformTypes:
            dif+=difDict[trform][i][0]
        difList+=[(dif,difDict[trform][i][1])]
    difList.sort()

    return difList

def SmartSortResults(difDict,casNums):
    tranformTypes=list(difDict.keys())[:]

    for trform in tranformTypes:
        difDict[trform].sort()
    difList=[]

    bestDict={}
    for i in range(len(casNums)):#casNum
        bestDict[casNums[i]]=[]

    for i in range(len(casNums)):
        tempList=[]
        for trform in tranformTypes:
            if bestDict[difDict[trform][i][1]]!="Done":
                bestDict[difDict[trform][i][1]]+=[(difDict[trform][i][0],trform)]
        for casNum in list(bestDict.keys()):
            if bestDict[casNum]!="Done":
                if len(bestDict[casNum])>=max(1,len(tranformTypes)//2+1):
                    dif=0
                    for comp in bestDict[casNum]:
                        dif=max(dif,comp[0])
                    tempList+=[(dif,casNum)]
                    bestDict[casNum]="Done"
        if tempList:
            tempList.sort()
            difList+=tempList

    return difList

class IRDB:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.realpath("IR.db"))
        self.cur = self.conn.cursor()

    def searchIRDB(self, sqlQuery):
        self.cur.execute(sqlQuery)
        return self.cur.fetchall()

    def writeIRDB(self, sqlWrite, dbValues=None):
        try:
            if dbValues:
                self.cur.execute(sqlWrite, dbValues)
            else:
                self.cur.execute(sqlWrite)
            return True
        except Exception as e:
            return False

    def commitIRDB(self):
        try:
            self.conn.commit()
            return True
        except Exception as e:
            return False

    def fetchallIRDB(self):
        return self.cur.fetchall()
#------------------------------------------------------------------------------
