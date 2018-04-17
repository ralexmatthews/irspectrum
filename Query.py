"""
Program: IRSpectrum.py
Programmed by: Josh Ellis, Josh Hollingsworth, Aaron Kruger, Alex Matthews, and
    Joseph Sneddon
Description: This program will recieve an IR Spectrograph of an unknown
    molecule and use our algorithm to compare that graph to a stored database of
    known molecules and their IR Spectrographs. This program will then return a
    list of the closest Spectrographs matches as determined by our algorithm.
"""
#---------------------------------Imports--------------------------------------
import PyPDF2
import time
import sys
import sqlite3
import warnings
import os
from os import path
from PIL import Image, ImageTk
from math import log
from IR_Functions import *
import multiprocessing as mp
#------------------------------------------------------------------------------

#---------------------------------Variables------------------------------------
#the range each axis of the graph covers
yMin=1.02
yMax=-0.05
yRange=yMax-yMin
xMin=200
xMax=4100
xRange=xMax-xMin

#the area of each image that we want (the graph)
targetRect=(113,978,29,724) #(left,right,top,bottom)
global Width
global Height

global graph
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------
#copies pixels from the source image within the targetRect
def cropRect(source,rect):
    #this with and height is standard for all IR samples
    Width=1024 #Local value
    Height=768 #Local value
    left,right,top,bottom=rect
    newImg=[]
    for y in range(top,bottom+1):
        for x in range(left,right+1):
            newImg+=[source[y*Width+x]]
    return newImg

 #checks if the pixel at x,y is black
def pix(x, y):
    global Width
    global graph
    r,g,b=graph[y*Width+x]
    if r+g+b>=100:
        return False#not black
    else:
        return True#black

"""
Creates a graphData list by finding each black pixel on the x axis. For each
x get the y range over which the graph has black pixels or None if the graph
is empty at that x value. It stores the min and max y values in the
graphData list. Then returns the filled graphData List.
"""
def drawGraph():
    global Width
    global Height
    graphData=[]#to be filled with values from graph
    for x in range(0,Width):
        graphData+=[None]
        foundPix=False#have you found a pixel while looping through the column
        for y in range(0,Height):
            p=pix(x, y)#is the pixel black
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
def convertToData(graphData):
    data=[]#final value written to file
    for x in range(len(graphData)):
        #Points in format x,y
        if graphData[x]:
            data+=[(convertx(x),
                    converty(graphData[x][0]),converty(graphData[x][1]))]

    return data

#convert graph x,y into scientific x,y
def convertx(x):
    global xMin
    global xRange
    global Width
    return xMin+xRange*(x/Width)

def converty(y):
    global yMin
    global yRange
    global Height
    return yMin+yRange*(y/Height)

#------------------------------------------------------------------------------

#----------------------------Multiprocessing functions-------------------------
def work(DataQ,ReturnQ,query,transformTypes):
    try:
        casNum,dataDict = DataQ.get()
        
        difDict={}
        for tType in transformTypes:
            difDict[tType]=[]

            #total the differences between the compound and the query
            # also draw an image to show this comparison
            dif=Compare(tType,dataDict[tType],query[tType])
                            
            difDict[tType]+=[(dif,casNum)]
        ReturnQ.put(difDict)
        return True
    except Exception as e:
        #uncomment to debug
        #'''
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('%s' % e)
        print("\n"+str(exc_tb.tb_lineno)+" "+str(exc_obj)+" "+str(exc_tb))
        #'''
        return False

def worker(workerNo,JobsDoneQ,NofJobs,NofWorkers,ReturnQ,DataQ,query,transformTypes):
    #Worker loop
    working=True
    while working:
        jobNo=JobsDoneQ.get()
        message=work(DataQ,ReturnQ,query,transformTypes)
        if NofJobs-jobNo<=NofWorkers-1:
            working=False

#------------------------------------------------------------------------------

#---------------------------------Program Main---------------------------------
def formatQueryData(queryPath):
    """ Open the source image """
    images = PullImages(queryPath)
    
    fname = queryPath.split("\\")[-1]
    fname = fname.split(".")[0]

    data=ReadGraph(images[0])
    os.remove(images[0])
    os.remove(queryPath)

    #calculate each transformation
    transformDict={}
    transformDict["cumulative"]=Cumulative([(e[0],e[2]) for e in data])

    return transformDict
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def compareQueryToDB(formatedQueryData):
    #only compare by cumulative for now
    transformTypes=["cumulative"]

    ## used to grab the total number of molecules
    conn = sqlite3.connect(os.path.realpath("IR.db"))
    sqlQ = "SELECT CAS_Num FROM IR_Raw GROUP BY CAS_Num"
    cur = conn.cursor()
    cur.execute(sqlQ)
    qData = cur.fetchall()

    sqlQ = "SELECT CAS_Num,Type,Wavelength,Value FROM IR_JoshEllisAlgorithm"
    cur = conn.cursor()
    cur.execute(sqlQ)
    data = cur.fetchall()

    dataDict={}
    
    for i in range(len(qData)):
        dataDict[qData[i][0]]={}
        for tType in transformTypes:
            dataDict[qData[i][0]][tType]=[]
    for i in range(len(data)):
        dataDict[data[i][0]][data[i][1]]+=[data[i][2:]]
    
    difDict={}
    for tType in formatedQueryData:
        difDict[tType]=[]
    
    CORES = mp.cpu_count()
    JobsDoneQ=mp.Queue()
    ReturnQ=mp.Queue()
    ReadRequestQ=mp.Queue()
    DataQ=mp.Queue()
    DataBuffer=CORES*2
    for i in range(len(qData)):
        JobsDoneQ.put(i+1)
        ReadRequestQ.put(1)
    for i in range(DataBuffer):
        DataQ.put((qData[i][0],dataDict[qData[i][0]]))
        ReadRequestQ.get()
        ReadRequestQ.put(0)
    
    p={}
    for i in range(CORES):
        p[i] = mp.Process(target = worker,\
            args=[i,JobsDoneQ,len(qData),CORES,ReturnQ,DataQ\
                  ,formatedQueryData,transformTypes])
        p[i].start()

    #Read returned data from workers, add new read reqests
    for i in range(DataBuffer,len(qData)+DataBuffer):
        retDict = ReturnQ.get()
        for tType in transformTypes:
            difDict[tType]+=retDict[tType]
        if ReadRequestQ.get():
            DataQ.put((qData[i][0],dataDict[qData[i][0]]))

    for i in range(CORES):
        p[i].join()

    #sort compounds by difference
    results=AddSortResults(difDict,[a[0] for a in qData])[:200]
    retString=""
    
    #save list of compound differences to file
    for i in range(len(results)):
        retString+=results[i][1]+" "

    #Gives sorted list of Output to main.js
    print(retString.strip())
          
    sys.stdout.flush()
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
if __name__ == "__main__":
    formatedQueryData = formatQueryData(sys.argv[1])
    
    compareQueryToDB(formatedQueryData)
#---------------------------------End of Program-------------------------------
