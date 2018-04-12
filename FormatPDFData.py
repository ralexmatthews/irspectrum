"""
This can be ran from the command line with the pdf file you wish to extract from
as an argument, it will save the image in the same directory you are in.
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
from IR_Functions import PullImages
#------------------------------------------------------------------------------

#---------------------------------Variables------------------------------------
#the range each axis of the graph covers
yMin=1.02
yMax=-0.05
yRange=yMax-yMin
xMin=200
xMax=4100
xRange=xMax-xMin
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------

#------------------------------------------------------------------------------

#---------------------------------Program Main---------------------------------
def formatPDFData(queryData):

    #copies pixels from the source image within the targetRect
    def cropRect(source,rect):
        #this with and height is standard for all IR samples
        Width=1024
        Height=768
        left,right,top,bottom=rect
        newImg=[]
        for y in range(top,bottom+1):
            for x in range(left,right+1):
                newImg+=[source[y*Width+x]]
        return newImg

    '''
    Create graphData list by reading pixels from graph
        -each entry in data is the range over wich each
         column has black pixels
    Scale to x and y units
    Save data to file
    '''
    #For each x get the y range over which the graph has black pixels
    # or None if the graph is empty at that x value
    def drawGraph(Width, Height):
        graphData=[]#to be filled with values from graph
        for x in range(0,Width):
            graphData+=[None]
            foundPix=False#have you found a pixel while looping through the column
            for y in range(0,Height):
                p=pix(x,y)#is the pixel black
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

    #checks if the pixel at x,y is black
    def pix(x,y):
        r,g,b=graph[y*Width+x]
        if r+g+b>=100:
            return False#not black
        else:
            return True#black

    #convert graph x,y into scientific x,y
    def convertx(x):
        global xMin
        global xRange
        return xMin+xRange*(x/Width)
    def converty(y):
        global yMin
        global yRange
        return yMin+yRange*(y/Height)

    def slopeSum(l):
        '''
        A new curve is created where element n is the sum of the first n terms in list l
         divided by the sum of all terms in l
        '''
        #for each point, add its value to all previous values in l
        retlist=[(0,0)]
        for point in l:
            retlist+=[(point[0],retlist[-1][1]+point[1])]
        retlist.pop(0)

        #normalize the new list by dividing each point by the last value
        for i in range(len(retlist)):
            retlist[i]=(retlist[i][0],retlist[i][1]/retlist[-1][1])

        #the returned list will have a range from 0 to 1
        return retlist

    '''
    The next two functions are attempts to transform the data in an IR graph
     into a more useful form. The "Transformations" are ment to be easily compared
     for two differnet compounds
    '''

    def peak(l):#peak to peak transformation
        '''
        Find all peaks in list l
        Weight peaks by their height and how far they are from other taller peaks
        '''
        retlist=[]
        lenl=len(l)
        for i in range(lenl):

            #current x and y values for point i in list l
            curx=l[i][0]
            cury=l[i][2]

            #If this point has the same y value as the previous point
            # then continue to the next point
            if i-1>=0: # and i+1<lenl
                if (l[i-1][2] == cury):
                    retlist+=[(curx,0)]
                    continue

            #Search right of the point until you run into another peak or off the graph
            # sum the difference between cury and the graph at i+j to find the area right of the peak
            s1=0
            j=1
            while i+j<lenl and l[i+j][2] <= cury and j<11:
                s1+= (cury - l[i+j][2]) * (l[i+j][0]-l[i+j-1][0])
                j+=1

            #Same opperation but searching left
            s2=0
            j=-1
            while i+j>=0 and l[i+j][2] <= cury and j>-11:
                s2+= (cury - l[i+j][2]) * (l[i+j+1][0]-l[i+j][0])
                j-=1

            #take the lowest of the 2 values
            #Note: log may not be useful. It was added to decrease the weight of tall peaks
            if min(s1,s2)>0:
                retlist+=[(curx,log(min(s1,s2)*cury+1,2))]
            else:#white 0 to new curve if the point was not a peak
                retlist+=[(curx,0)]

        return retlist

    def absD(l):#Transformation based on slope
        '''
        The absolute value of the slope of the curve in list l
        Note: this method may not be useful for matching compounds
        '''
        retlist=[]
        for i in range(len(l)):
            retlist+=[(l[i][0],l[i][2]-l[i][1])]

        return retlist

    #TODO The drawPix, devertx, and deverty functions appear to no longer be used
    #function to draw pixels
    def drawPix(x,y,c):
        graph[int(y*Width+x)]=c

    #convert graph x,y into scientific x,y
    def devertx(x):
        global xMin
        global xRange
        return round((x-xMin)/xRange*Width)
    def deverty(y):
        global yMin
        global yRange
        return round((y-yMin)/yRange*Height)

    addToDB = False #TODO Will delete this later.

    #the area of each image that we want (the graph)
            #(left,right,top,bottom)
    targetRect=(113,978,29,724)
    #width and height of out cropped graph
    Width=targetRect[1]-targetRect[0]+1
    Height=targetRect[3]-targetRect[2]+1

    path = "C:\\Users\\Josh\\Desktop\\Programming\\CSC 450\\irspectrum\\temp\\55-21-0.pdf"
    dest=os.path.join("data", "Query")
    """ Open the source image """
    images = PullImages(queryData)
    #images = PullImages(path)

    fname = queryData.split("\\")[-1]
    #fname = path.split("\\")[-1]
    fname = fname.split(".")[0]

    """ is this file already in the database? """
    conn = sqlite3.connect(os.path.realpath("IR.db"))
    sqlQ = "SELECT CAS_Num FROM IR_Raw WHERE CAS_Num='"+fname+"'"
    cur = conn.cursor()
    cur.execute(sqlQ)
    qData = cur.fetchall()

    """ if not in the database set the flag to add it """
    if len(qData)==0:
        addToDB = True

    """ Crop the image """
    img = Image.open(images[0])
    imgdata=list(img.getdata())#the pixels from the image

    #the graph cut out of the larger image
    graph=cropRect(imgdata,targetRect)

    #Draws a graph of each (x, y) point found in the image.
    graphData = drawGraph(Width, Height)

    #Converts graph to the final values that will be stored in the DB.
    data = convertToData(graphData)

    #save data
    f = open(dest+".data", "w")
    sqlQ = "INSERT INTO IR_Raw(CAS_Num, Wavelength, x_min, x_max) VALUES (?, ?, ?, ?)"

    for element in data:
        if addToDB:
            dbvalues = (fname, element[0], element[1], element[2])
            cur = conn.cursor()
            cur.execute(sqlQ, dbvalues)
        f.write(str(element[0])+","+str(element[1])+","+str(element[2])+'\n')
    f.close()
    if addToDB:
        conn.commit()

    #TODO delete these values since they are never used after new assignment.
    #Height and Width of the part of the graph containing data
    #Width=866
    #Height=696

    #calculate each transformation
    transformDict={}
    transformDict["peak"]=slopeSum(peak(data))
    transformDict["absD"]=slopeSum(absD(data))
    transformDict["basic"]=slopeSum( [(e[0],e[2]) for e in data])

    sqlQ = "INSERT INTO IR_JoshEllisAlgorithm(CAS_Num, Type, Wavelength, Value) VALUES (?, ?, ?, ?)"
    #save each transformation to file
    for k in transformDict:
        d=[]
        for each in transformDict[k]:
            d+=[str(each[0])+','+str(each[1])]
            if addToDB: # add stuff to DB if doesn't exist
                dbvalues = (fname, k, each[0], each[1])
                cur = conn.cursor()
                cur.execute(sqlQ, dbvalues)
            #save data
            f = open(dest+"."+k, "w")
            for element in d:
                f.write(str(element) + '\n')
            f.close()
    if addToDB:
        conn.commit()
        addToDB = False
    #print(dest)

    #sys.stdout.flush()

formatPDFData(sys.argv[1])
#---------------------------------End of Program-------------------------------
