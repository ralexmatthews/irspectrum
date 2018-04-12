"""
This can be ran from the command line with the pdf file you wish to extract from
as an argument, it will save the image in the same directory you are in.
"""
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

filedir=[os.path.join("IR samples",file) for file in os.listdir("IR samples") if file.endswith(".pdf")]
for file in filedir:
    
    """ Open the source image """
    images = PullImages(file)

    addToDB = False

    #print(file)
    fname = file.split("\\")[-1]
    #print(fname)
    #fname = path.split("\\")[-1]
    fname = fname.split(".")[0]
    #print(fname,"\n")

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

    #save data
    #f = open(dest+".data", "w")
    sqlQ = "INSERT INTO IR_Raw(CAS_Num, Wavelength, x_min, x_max) VALUES (?, ?, ?, ?)"

    for element in data:
        if addToDB:
            dbvalues = (fname, element[0], element[1], element[2])
            cur = conn.cursor()
            cur.execute(sqlQ, dbvalues)
        #f.write(str(element[0])+","+str(element[1])+","+str(element[2])+'\n')
    #f.close()
    if addToDB:
        conn.commit()

    #Height and Width of the part of the graph containing data
    Width=866
    Height=696
    
    #calculate each transformation
    transformDict={}
    transformDict["absD"]=slopeSum(absD(data))
    transformDict["basic"]=slopeSum( [(e[0],e[2]) for e in data])
    transformDict["peak"]=peak(data)

    #function to draw pixels
    def drawPix(x,y,c):
        graph[int(y*Width+x)]=c

    #convert graph x,y into scientific x,y
    def devertx(x):
        return round((x-xMin)/xRange*Width)
    def deverty(y):
        return round((y-yMin)/yRange*Height)

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
            '''
            f = open(dest+"."+k, "w")
            for element in d:
                f.write(str(element) + '\n')
            f.close()
            '''
    if addToDB:
        print(fname, "added to DB")
        conn.commit()
        addToDB = False
    else:
        print(fname, "already in DB")
        
