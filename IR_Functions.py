import PyPDF2

import sys
import warnings
import os
from os import path
from math import log

warnings.filterwarnings("ignore")

number = 0

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
"""
def slopeSum(l):
    
    '''
    A new curve is created where element n is the sum of the first n terms in list l
     divided by the sum of all terms in l
    '''

    def avgPoints(p1,p2,x):
        x1=int(p1[0])
        x2=int(p2[0])
        d=abs(x1-x2)
        if d==0:
            return max(p1[1],p2[1])
        return p1[1]*(d-abs(p1[0]-x))/d+p2[1]*(d-abs(p2[0]-x))/d
    
    #for each point, add its value to all previous values in l
    retlist=[(0,0)]
    t=l[:]+[(4051,l[-1][1])]
    i=0
    for x in range(4050):
        #print(t[0],x)
        y=avgPoints(t[0],t[1],x)
        retlist+=[(x,retlist[-1][1]+y)]
        while x>int(t[0][0]):
            t.pop(0)
        if len(t)==1:
            break

    #normalize the new list by dividing each point by the last value
    for i in range(len(retlist)):
        retlist[i]=(retlist[i][0],retlist[i][1]/retlist[-1][1])

    #the returned list will have a range from 0 to 1
    return retlist
#"""
'''
The next two functions are attempts to transform the data in an IR graph
 into a more useful form. The "Transformations" are ment to be easily compared
 for two differnet compounds
'''
"""
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
"""
def peak(l):
    l=l[:]#derefrence
    l=[[a[0],a[2]] for a in l]#remove min
    Peaks=[]
    numLeft=len(l)
    while numLeft:
        highest=(0,-1)
        for i in range(len(l)):
            if l[i]:
                if l[i][1]>highest[1]:
                    highest=(i,l[i][1])
        i=highest[0]
        j=i
        localLow=highest[1]
        while j>0 and l[j-1]:
            j-=1
            if l[i][1]>localLow:
                break
            localLow=l[j][1]
            l[j]=None
            numLeft-=1
        j=i
        localLow=highest[1]
        while j<len(l)-1 and l[j+1]:
            j+=1
            if l[i][1]>localLow:
                break
            localLow=l[j][1]
            l[j]=None
            numLeft-=1
        Peaks+=[l[i]]
        l[i]=None
        numLeft-=1
    return Peaks

def absD(l):#Transformation based on slope
    '''
    The absolute value of the slope of the curve in list l
    Note: this method may not be useful for matching compounds
    '''
    retlist=[]
    for i in range(len(l)):
        retlist+=[(l[i][0],l[i][2]-l[i][1])]
                
    return retlist

def compare(tType,transformation1,transformation2):
    dif=0
    if tType!="peak":
        for a in range(min(len(transformation1),len(transformation2))):
            dif+=abs(transformation1[a][1]-transformation2[a][1])**2
    else:
        #Swap if needed, make t1 sorter than t2
        if len(transformation1)>len(transformation2):
            t=transformation1[:]
            transformation1=transformation2[:]
            transformation2=t

        len1=len(transformation1)
        len2=len(transformation2)
        def posdif(x1,x2):
            return abs(x1-x2)
        def rankdif(i1,n1,i2,n2):
            return abs(i1/n1-i2/n2)
        def hightdif(y1,h1,y2,h2):
            return abs(y1/h1-y2/h2)
        
        for j in range(len1):
            closest=0
            d=999999999999999
            for k in range(len2):
                if transformation2[k]:
                    p=posdif(transformation1[j][0],transformation2[k][0])
                    t=(p*(rankdif(j,len1,k,len2)))
                    if t<d:
                        closest=k
                        d=t
            transformation2[closest]=None
            dif+=d/(j+1)#(j/len1+1)
        for k in range(len2):
            if transformation2[k]:
                closest=0
                d=999999999999999
                for j in range(len1):
                    if transformation1[j]:
                        p=posdif(transformation1[j][0],transformation2[k][0])
                        t=(p*(rankdif(j,len1,k,len2)))
                        if t<d:
                            closest=j
                            d=t
                transformation1[closest]=None
                dif+=d/(k+1)#(j/len1+1)
        dif=dif*1000/(len1+len2)
    return dif
