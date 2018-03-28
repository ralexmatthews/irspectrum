"""
This can be ran from the command line with the pdf file you wish to extract from
as an argument, it will save the image in the same directory you are in.
"""
import PyPDF2

import time

import sys
import warnings
import os
from os import path
from PIL import Image, ImageTk
from math import log

from IR_Functions import PullImages

Query=False
Debug=False

if len(sys.argv)==1:
    filedir=[os.path.join("IR samples",file) for file in os.listdir("IR samples") if file.endswith(".pdf")]
    filedir+=[os.path.join("query",file) for file in os.listdir("query") if file==("Query.pdf")]
else:
    filedir=[sys.argv[1]]
    if "-query" in sys.argv[2:]: Query=True
    if "-debug" in sys.argv[2:]: Debug=True

for file in filedir:

    if "\\" in file:
        fname=file.split("\\")[-1]
    else:
        fname=file.split("/")[-1]

    if Query:
        dest=os.path.join("query",str(int(time.time())) )
    else:
        dest=os.path.join("data",fname)
        
    
    images = PullImages(file)
    
    '''
    Open the source image
    Crop the image
    '''

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
    f = open(dest+".data", "w")
    for element in data:
        f.write(str(element[0])+","+str(element[1])+","+str(element[2])+'\n')
    f.close()

    #Height and Width of the part of the graph containing data
    Width=866
    Height=696

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

    #calculate each transformation
    transformDict={}
    transformDict["peak"]=slopeSum(peak(data))
    transformDict["absD"]=slopeSum(absD(data))
    transformDict["basic"]=slopeSum( [(e[0],e[2]) for e in data])

    #function to draw pixels
    def drawPix(x,y,c):
        graph[int(y*Width+x)]=c

    #convert graph x,y into scientific x,y
    def devertx(x):
        return round((x-xMin)/xRange*Width)
    def deverty(y):
        return round((y-yMin)/yRange*Height)

    #save each transformation to file
    for k in transformDict:
        d=[]
        for each in transformDict[k]:
            d+=[str(each[0])+','+str(each[1])]
            #save data
            f = open(dest+"."+k, "w")
            for element in d:
                f.write(str(element) + '\n')
            f.close()
    
    if Debug:    
        graph=[]#image for the graph

        #fill graph with a blank white image of size Width x Height
        for x in range(Width):
            for y in range(Height):
                graph+=[(255,255,255)]

        

        for i in range(len(data)):#draw lines in graph from data
            
            datapoint=data[i]
            #calculate the x,y of the origional IR graph from data
            if datapoint:
                x=devertx(datapoint[0])
                for y in range(deverty(datapoint[2]),deverty(datapoint[1])):
                    graph[int(y*Width+x)]=(0,0,0)#draw points in graph at x

            #draw each of the transformations on to the graph
            drawPix(devertx(transformDict["peak"][i][0]), deverty(transformDict["peak"][i][1]/transformDict["peak"][-1][1]),(255,0,0))
            drawPix(devertx(transformDict["absD"][i][0]), deverty(transformDict["absD"][i][1]/transformDict["absD"][-1][1]),(0,0,255))
            drawPix(devertx(transformDict["basic"][i][0]), deverty(transformDict["basic"][i][1]/transformDict["basic"][-1][1]),(0,255,0))

        #save graph with transformations
        img = Image.new('RGB', (Width, Height))
        img.putdata(graph)
        img.save(dest+'.transform.png')

print(dest)

sys.stdout.flush()
