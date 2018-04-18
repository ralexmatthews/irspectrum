
'''###############################################################'''
'''jpegExtract.py'''
'''###############################################################'''

"""
This can be ran from the command line with the pdf file you wish to extract from
as an argument, it will save the image in the same directory you are in.
"""
import PyPDF2

from PIL import Image

import sys
from os import path
import warnings
warnings.filterwarnings("ignore")

number = 0

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
    filename = sys.argv[1]
    abspath = path.abspath(filename)
except BaseException:
    print('Usage :\nPDF_extract_images file.pdf page1 page2 page3 …')
    sys.exit()


file = PyPDF2.PdfFileReader(open(filename, "rb"))

page0 = file.getPage(0)

p = 1
images=recurse(p, page0)

#print('%s extracted images'% number)

'''###############################################################'''
'''IR_read_graph.py'''
'''###############################################################'''

'''
Open the source image
Crop the image
'''

img = Image.open(images[0])
imgdata=list(img.getdata())#the pixels from the image

#this with and height seems to be standard for all IR samples
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
def convertx(x):
    return xMin+xRange*(x/Width)
def converty(y):
    return yMin+yRange*(y/Height)

data=[]#final value written to file
#convert graph into datapoints
for x in range(len(graphData)):
    if graphData[x]:
        #Points in format x,y
        data+=[str(convertx(x))+','
               +str( converty( (graphData[x][0]+graphData[x][0])/2 ) )]                 

#save data
f = open("data.txt", "w")
for element in data:
    f.write(str(element) + '\n')
f.close()

print('done')
