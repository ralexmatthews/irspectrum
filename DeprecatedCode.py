#---------------------------------Deprecated Code------------------------------
"""#TODO Where is str2Tuple() function being used?
def str2Tuple(s):#convert strings to 2 element tuples (float,float)
    if (s=='None'):
        return None
    else:
        x,y =s.split(',')
        return tuple(map(float,[x,y]))"""
"""#the range each axis of the graph covers
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

global graph"""
"""
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
"""
Creates a graphData list by finding each black pixel on the x axis. For each
x get the y range over which the graph has black pixels or None if the graph
is empty at that x value. It stores the min and max y values in the
graphData list. Then returns the filled graphData List.
"""
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
"""
#fname = queryPath.split("\\")[-1]
#fname = fname.split(".")[0]
"""
path = "C:\\Users\\Josh\\Desktop\\Programming\\CSC 450\\irspectrum\\temp\\55-21-0.pdf"
#images = PullImages(path)
#fname = path.split("\\")[-1]
"""
""" is this file already in the database? """
"""addToDB = False #TODO Will delete this later.
dest=os.path.join("data", "Query")
conn = sqlite3.connect(os.path.realpath("IR.db"))"""
#sqlQ = "SELECT CAS_Num FROM IR_Raw WHERE CAS_Num='"+fname+"'"
"""cur = conn.cursor()
cur.execute(sqlQ)
qData = cur.fetchall()"""

""" if not in the database set the flag to add it """
"""if len(qData)==0:
    addToDB = True"""
#save data
#f = open(dest+".data", "w")
#sqlQ = "INSERT INTO IR_Raw(CAS_Num, Wavelength, x_min, x_max) VALUES (?, ?, ?, ?)"
"""for element in data:
    if addToDB:
        dbvalues = (fname, element[0], element[1], element[2])
        cur = conn.cursor()
        cur.execute(sqlQ, dbvalues)
    f.write(str(element[0])+","+str(element[1])+","+str(element[2])+'\n')
f.close()
if addToDB:
    conn.commit()"""
"""d+=[str(each[0])+','+str(each[1])]
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
addToDB = False"""

"""
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
"""
#print(transformation1)
#size of graph images
#Width=866
#Height=696
#file2="Query."+tType
#read data for the query
#f = open(os.path.join("data",file2), "r")
#lines=f.readlines()
#[str2Tuple(s.strip()) for s in lines]
#transformation2= formatedQueryData
"""
#numbers used to convert from graph x,y to scientific x,y
yMin=1.02
yMax=-0.05
yRange=yMax-yMin
xMin=200
xMax=4100
xRange=xMax-xMin

def devertx(x):
    return round((x-xMin)/xRange*Width)
def deverty(y):
    return round((y-yMin)/yRange*Height)

graph=[]
#create graph as black blank image
for x in range(Width):
    for y in range(Height):
        graph+=[(0,0,0)]

#draw a pixel
def addPix(x,y,c):
    r,g,b=c
    oR,oG,oB = graph[int(y*Width+x)]
    graph[int(y*Width+x)]=min(255,r+oR),min(255,g+oG),min(255,b+oB)
"""
#read data for the compound
"""f = open(os.path.join("data",file1), "r")
lines=f.readlines()
transformation1=[str2Tuple(s.strip()) for s in lines]"""
'''
f = open("output\\"+file1.split(".")[0]+tType+'.comp.txt', "w")
f.write(file1+" x "+file2 + '\n')
f.write("difference = "+ str(dif) + '\n')
f.close()
'''
#TODO delete these three lines if filedir is never used.
#list of all compounds
#filedir=[file for file in os.listdir("IR samples") if file.endswith(".pdf") and file!="Query1.pdf"]
#------------------------------------------------------------------------------
