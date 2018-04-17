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
from IR_Functions import PullImages
#------------------------------------------------------------------------------

#---------------------------------Variables------------------------------------
# the range each axis of the graph covers
yMin = 1.02
yMax = -0.05
yRange = yMax-yMin
xMin = 200
xMax = 4100
xRange = xMax-xMin

# the area of each image that we want (the graph)
targetRect = (113, 978, 29, 724)  # (left,right,top,bottom)
global Width
global Height

global graph
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------
# copies pixels from the source image within the targetRect


def cropRect(source, rect):
    # this with and height is standard for all IR samples
    Width = 1024  # Local value
    Height = 768  # Local value
    left, right, top, bottom = rect
    newImg = []
    for y in range(top, bottom+1):
        for x in range(left, right+1):
            newImg += [source[y*Width+x]]
    return newImg

 # checks if the pixel at x,y is black


def pix(x, y):
    global Width
    global graph
    r, g, b = graph[y*Width+x]
    if r+g+b >= 100:
        return False  # not black
    else:
        return True  # black


"""
Creates a graphData list by finding each black pixel on the x axis. For each
x get the y range over which the graph has black pixels or None if the graph
is empty at that x value. It stores the min and max y values in the
graphData list. Then returns the filled graphData List.
"""


def drawGraph():
    global Width
    global Height
    graphData = []  # to be filled with values from graph
    for x in range(0, Width):
        graphData += [None]
        foundPix = False  # have you found a pixel while looping through the column
        for y in range(0, Height):
            p = pix(x, y)  # is the pixel black
            if p and not foundPix:
                # record the first black pixels y value
                foundPix = True
                maxVal = y
            elif not p and foundPix:
                # record the last black pixels y value
                minVal = y
                graphData[-1] = (minVal, maxVal)  # write these values to data
                break  # next x

    return graphData

# convert graph into datapoints


def convertToData(graphData):
    data = []  # final value written to file
    for x in range(len(graphData)):
        # Points in format x,y
        if graphData[x]:
            data += [(convertx(x),
                      converty(graphData[x][0]), converty(graphData[x][1]))]

    return data

# convert graph x,y into scientific x,y


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


def slopeSum(l):
    '''
    A new curve is created where element n is the sum of the first n terms in list l
     divided by the sum of all terms in l
    '''
    # for each point, add its value to all previous values in l
    retlist = [(0, 0)]
    for point in l:
        retlist += [(point[0], retlist[-1][1]+point[1])]
    retlist.pop(0)

    # normalize the new list by dividing each point by the last value
    for i in range(len(retlist)):
        retlist[i] = (retlist[i][0], retlist[i][1]/retlist[-1][1])

    # the returned list will have a range from 0 to 1
    return retlist


'''
The next two functions are attempts to transform the data in an IR graph
 into a more useful form. The "Transformations" are ment to be easily compared
 for two differnet compounds
'''


def peak(l):  # peak to peak transformation
    '''
    Find all peaks in list l
    Weight peaks by their height and how far they are from other taller peaks
    '''
    retlist = []
    lenl = len(l)
    for i in range(lenl):

        # current x and y values for point i in list l
        curx = l[i][0]
        cury = l[i][2]

        # If this point has the same y value as the previous point
        # then continue to the next point
        if i-1 >= 0:  # and i+1<lenl
            if (l[i-1][2] == cury):
                retlist += [(curx, 0)]
                continue

        # Search right of the point until you run into another peak or off the graph
        # sum the difference between cury and the graph at i+j to find the area right of the peak
        s1 = 0
        j = 1
        while i+j < lenl and l[i+j][2] <= cury and j < 11:
            s1 += (cury - l[i+j][2]) * (l[i+j][0]-l[i+j-1][0])
            j += 1

        # Same opperation but searching left
        s2 = 0
        j = -1
        while i+j >= 0 and l[i+j][2] <= cury and j > -11:
            s2 += (cury - l[i+j][2]) * (l[i+j+1][0]-l[i+j][0])
            j -= 1

        # take the lowest of the 2 values
        # Note: log may not be useful. It was added to decrease the weight of tall peaks
        if min(s1, s2) > 0:
            retlist += [(curx, log(min(s1, s2)*cury+1, 2))]
        else:  # white 0 to new curve if the point was not a peak
            retlist += [(curx, 0)]

    return retlist


def absD(l):  # Transformation based on slope
    '''
    The absolute value of the slope of the curve in list l
    Note: this method may not be useful for matching compounds
    '''
    retlist = []
    for i in range(len(l)):
        retlist += [(l[i][0], l[i][2]-l[i][1])]

    return retlist


def str2Tuple(s):  # convert strings to 2 element tuples (float,float)
    if (s == 'None'):
        return None
    else:
        x, y = s.split(',')
        return (float(x), float(y))
#------------------------------------------------------------------------------

#---------------------------------Program Main---------------------------------


def formatQueryData(queryData):
    """ Open the source image """
    images = PullImages(queryData)
    fname = queryData.split("\\")[-1]
    fname = fname.split(".")[0]

    """ Crop the image """
    img = Image.open(images[0])

    # save the image so client can display uploaded image
    if path.isfile(path.realpath('./public/images/temp.jpg')):
        os.remove(path.realpath('./public/images/temp.jpg'))
    img.save(path.realpath('./public/images/temp.jpg'))

    # the pixels from the image
    imgdata = list(img.getdata())

    # the graph cut out of the larger image
    global targetRect
    global graph
    graph = cropRect(imgdata, targetRect)

    # width and height of out cropped graph
    global Width
    Width = targetRect[1]-targetRect[0]+1
    global Height
    Height = targetRect[3]-targetRect[2]+1

    # Draws a graph of each (x, y) point found in the image.
    graphData = drawGraph()

    # Converts graph to the final values that will be stored in the DB.
    data = convertToData(graphData)

    # calculate each transformation
    transformDict = {}
    # transformDict["peak"]=slopeSum(peak(data))
    transformDict["absD"] = slopeSum(absD(data))
    #transformDict["basic"]=slopeSum( [(e[0],e[2]) for e in data])

    #sqlQ = "INSERT INTO IR_JoshEllisAlgorithm(CAS_Num, Type, Wavelength, Value) VALUES (?, ?, ?, ?)"
    # save each transformation to file
    formatedQueryData = []
    for k in transformDict:
        for each in transformDict[k]:
            formatedQueryData.append((each[0], each[1]))

    return formatedQueryData
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------


def compareQueryToDB(formatedQueryData):
    # list of total diffence for each compound
    difList = []

    # only compare by peak for now
    #tranformTypes={"peak": (255,0,0), "basic": (0,255,0),"absD":(0,0,255)}
    #tranformTypes={"peak": (255,0,0), "basic": (0,255,0)}
    tranformTypes = {"absD": (0, 0, 255)}
    #tranformTypes={"peak": (255,0,0)}
    #tranformTypes={"basic": (0,255,0)}

    # used to grab the total number of molecules
    conn = sqlite3.connect(os.path.realpath("IR.db"))
    sqlQ = "SELECT CAS_Num FROM IR_Raw GROUP BY CAS_Num"
    cur = conn.cursor()
    cur.execute(sqlQ)
    qData = cur.fetchall()

    for i in range(len(qData)):

        difference = 0
        for tType in tranformTypes:
            sqlQ = "SELECT Wavelength, Value FROM IR_JoshEllisAlgorithm WHERE CAS_Num=? AND Type=?"
            cur = conn.cursor()
            cur.execute(sqlQ, (qData[i][0], tType))
            transformation1 = cur.fetchall()

            dif = 0
            # total the differences between the compound and the query
            # also draw an image to show this comparison
            for a in range(min(len(transformation1), len(formatedQueryData))):
                dif += abs(transformation1[a][1]-formatedQueryData[a][1])

            difference += dif

        difList += [(difference, i)]

    # sort compounds by difference
    difList.sort()

    retString = ""

    # save list of compound differences to file
    f = open(os.path.join("output", 'Ranked Differences.txt'), "w")
    for i in range(len(difList)):
        f.write('#'+str(i+1)+': '+qData[difList[i][1]][0]+'.pdf\n')
        retString += qData[difList[i][1]][0]+" "
        f.write("difference = " + str(difList[i][0]) + '\n\n')
    f.close()

    results = retString.strip()
    # Gives sorted list of Output to main.js
    print(results)

    sys.stdout.flush()
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
formatedQueryData = formatQueryData(sys.argv[1])

compareQueryToDB(formatedQueryData)
#---------------------------------End of Program-------------------------------
