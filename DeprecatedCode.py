#---------------------------------Deprecated Code------------------------------
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
