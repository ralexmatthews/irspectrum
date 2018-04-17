"""

"""
#---------------------------------Imports--------------------------------------
import PyPDF2
from PIL import Image, ImageTk
import sys
import warnings
import os
from os import path
from shutil import copyfile
import PyPDF2
import sys
import sqlite3
import warnings
import os
from os import path
from PIL import Image, ImageTk
from math import log
from shutil import copyfile

import multiprocessing as mp

import time
warnings.filterwarnings("ignore")
#------------------------------------------------------------------------------

#---------------------------------Variables------------------------------------
#global variables go here
number = 0
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------

def str2Tuple(s):#convert strings to 2 element tuples (float,float)
    if (s=='None'):
        return None
    else:
        x,y =s.split(',')
        return tuple(map(float,[x,y]))

def PullImages(filename):

    '''
    Pull graph images from PDF's
    '''
    def recurse(page, xObject):
        global number

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

                #imagename = "%s"%(abspath[:-4], p, obj[1:])

                if xObject[obj]['/Filter'] == '/FlateDecode':
                    img = Image.frombytes(mode, size, data)
                    img.save(filename + ".png")
                    number += 1
                    images+=[filename + ".png"]
                elif xObject[obj]['/Filter'] == '/DCTDecode':
                    img = open(filename + ".jpg", "wb")
                    img.write(data)
                    img.close()
                    number += 1
                    images+=[filename + ".jpg"]
                elif xObject[obj]['/Filter'] == '/JPXDecode':
                    img = open(filename + ".jp2", "wb")
                    img.write(data)
                    img.close()
                    number += 1
                    images+=[filename + ".jp2"]
            else:
                recurse(page, xObject[obj])
        return images

    try:
        abspath = path.abspath(filename)
    except BaseException:
        print('Usage :\nPDF_extract_images file.pdf page1 page2 page3 …')
        sys.exit()

    f = PyPDF2.PdfFileReader(open(filename, "rb"))

    page0 = f.getPage(0)
    p = 1

    images=recurse(p, page0)

    return images

def ReadGraph(image):
    """ Crop the image """
    img = Image.open(image)
    imgdata=list(img.getdata())#the pixels from the image

    #this with and height is standard for all IR samples
    Width=1024
    Height=768

    #the area of each image that we want (the graph)
            #(left,right,top,bottom)
    targetRect=(113,978,29,724)

    def cropRect(source,rect):#copies pixels from the source image within the targetRect
        left,right,top,bottom=rect
        newImg=[]
        for y in range(top,bottom+1):
            for x in range(left,right+1):
                newImg+=[source[y*Width+x]]
        return newImg

    #the graph cut out of the larger image
    graph=cropRect(imgdata,targetRect)

    #width and height of out cropped graph
    Width=targetRect[1]-targetRect[0]+1
    Height=targetRect[3]-targetRect[2]+1

    '''
    Create graphData list by reading pixels from graph
        -each entry in data is the range over wich each
         column has black pixels
    Scale to x and y units
    Save data to file
    '''

    graphData=[]#to be filled with values from graph

    def pix(x,y):#checks if the pixel at x,y is black
        r,g,b=graph[y*Width+x]
        if r+g+b>=100:
            return False#not black
        else:
            return True#black

    #For each x get the y range over which the graph has black pixels
    # or None if the graph is empty at that x value
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

    #the range each axis of the graph covers
    yMin=1.02
    yMax=-0.05
    yRange=yMax-yMin
    xMin=200
    xMax=4100
    xRange=xMax-xMin

    #convert graph x,y into scientific x,y
    def convertx(x):
        return xMin+xRange*(x/Width)
    def converty(y):
        return yMin+yRange*(y/Height)

    data=[]#final value written to file
    #convert graph into datapoints
    for x in range(len(graphData)):
        #Points in format x,y
        if graphData[x]:
            data+=[(convertx(x),
                    converty(graphData[x][0]),converty(graphData[x][1]))]
    return(data)

def Cumulative(l):
    l=['x']+l[:]+['x']
    scanrange=20
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

def Compare(tType,transformation1,transformation2):
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
        bestDict[casNums]=[]

    for i in range(len(casNums)):
        tempList=[]
        for trform in tranformTypes:
            print(i,trform,difDict[trform][i][1])
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

#------------------------------------------------------------------------------
