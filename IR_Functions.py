"""
"""
#---------------------------------Imports--------------------------------------
import PyPDF2
import sys
import warnings
import os
from os import path
warnings.filterwarnings("ignore")
#------------------------------------------------------------------------------

#---------------------------------Variables------------------------------------
# global variables go here
number = 0
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------


def str2Tuple(s):  # convert strings to 2 element tuples (float,float)
    if (s == 'None'):
        return None
    else:
        x, y = s.split(',')
        return tuple(map(float, [x, y]))


def PullImages(filename):
    '''
    Pull graph images from PDF's
    '''
    def recurse(page, xObject):
        global number

        xObject = xObject['/Resources']['/XObject'].getObject()

        images = []

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
                    images += [filename + ".png"]
                elif xObject[obj]['/Filter'] == '/DCTDecode':
                    img = open(filename + ".jpg", "wb")
                    img.write(data)
                    img.close()
                    number += 1
                    images += [filename + ".jpg"]
                elif xObject[obj]['/Filter'] == '/JPXDecode':
                    img = open(filename + ".jp2", "wb")
                    img.write(data)
                    img.close()
                    number += 1
                    images += [filename + ".jp2"]
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

    images = recurse(p, page0)

    return images


def Cumulative(l):
    l = ['x']+l[:]+['x']
    scanrange = 20
    divisor = 0
    total = 0
    for i in range(1, scanrange+1):
        divisor += max(0.1, l[i][1])
    retlist = []
    for i in range(1, len(l)-1):

        low = max(0, i-scanrange)
        high = min(len(l)-1, i+scanrange)

        total -= max(0.1, l[low][1]) if l[low] != "x" else 0
        total += max(0.1, l[i][1]) if l[i] != "x" else 0

        divisor -= max(0.1, l[low][1]) if l[low] != "x" else 0
        divisor += max(0.1, l[high][1]) if l[high] != "x" else 0

        retlist += [(l[i][0], total/divisor)]

    return retlist


def Compare(tType, transformation1, transformation2):
    dif = 0
    # Swap if needed, want t1 to be sorter than t2
    if len(transformation1) > len(transformation2):
        tmp = transformation1[:]
        transformation1 = transformation2[:]
        transformation2 = tmp

    k = 0
    for j in range(len(transformation1)):
        while transformation1[j][0] > transformation2[k][0] and k < len(transformation2)-1:
            k += 1
        dif += abs(transformation1[j][1]-transformation2[k][1])

    return dif


def AddSortResults(difDict, casNums):
    tranformTypes = list(difDict.keys())[:]

    difList = []
    for i in range(len(casNums)):
        dif = 0
        for trform in tranformTypes:
            dif += difDict[trform][i][0]
        difList += [(dif, difDict[trform][i][1])]
    difList.sort()

    return difList


def SmartSortResults(difDict, casNums):
    tranformTypes = list(difDict.keys())[:]

    for trform in tranformTypes:
        difDict[trform].sort()
    difList = []

    bestDict = {}
    for i in range(len(casNums)):  # casNum
        bestDict[casNums] = []

    for i in range(len(casNums)):
        tempList = []
        for trform in tranformTypes:
            print(i, trform, difDict[trform][i][1])
            if bestDict[difDict[trform][i][1]] != "Done":
                bestDict[difDict[trform][i][1]
                         ] += [(difDict[trform][i][0], trform)]
        for casNum in list(bestDict.keys()):
            if bestDict[casNum] != "Done":
                if len(bestDict[casNum]) >= max(1, len(tranformTypes)//2+1):
                    dif = 0
                    for comp in bestDict[casNum]:
                        dif = max(dif, comp[0])
                    tempList += [(dif, casNum)]
                    bestDict[casNum] = "Done"
        if tempList:
            tempList.sort()
            difList += tempList

    return difList

#------------------------------------------------------------------------------
