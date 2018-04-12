import sys
import sqlite3
import os
from os import path
from PIL import Image, ImageTk
from math import log

import time as T

from IR_Functions import *

#size of graph images
Width=866
Height=696

#list of all compounds
filedir=[file for file in os.listdir("IR samples") if file.endswith(".pdf") and file!="Query1.pdf"]

#list of total diffence for each compound
difList=[]

tranformTypes=["peak","basic","absD"]
#tranformTypes=["basic","absD"]
#tranformTypes=["basic"]
#tranformTypes=["peak"]
#tranformTypes=["absD"]


## used to grab the total number of molecules
conn = sqlite3.connect(os.path.realpath("IR.db"))
sqlQ = "SELECT CAS_Num FROM IR_Raw GROUP BY CAS_Num"
cur = conn.cursor()
cur.execute(sqlQ)
qData = cur.fetchall()
#############

#print(qData)

startTime = T.time()

difDict={}
for tType in tranformTypes:
    difDict[tType]=[]
    for i in range(len(qData)):
    
        sqlQ = "SELECT Wavelength, Value FROM IR_JoshEllisAlgorithm WHERE CAS_Num=? AND Type=?"
        cur = conn.cursor()
        cur.execute(sqlQ, (qData[i][0], tType))
        transformation1 = cur.fetchall()
        
        file2="Query."+tType

        def str2Tuple(s):#convert strings to 2 element tuples (float,float)
            
            if s=='None':
                return None
            
            x,y =s. split(',')
            return ( float(x) , float(y) )

        #read data for the compound
        """f = open(os.path.join("data",file1), "r")
        lines=f.readlines()
        transformation1=[str2Tuple(s.strip()) for s in lines]"""

        #read data for the query
        f = open(os.path.join("data",file2), "r")
        lines=f.readlines()
        transformation2=[str2Tuple(s.strip()) for s in lines]
        #print(transformation1)
   
        #total the differences between the compound and the query
        # also draw an image to show this comparison
        dif=compare(tType,transformation1,transformation2)
                        
        #                 dif    casNum
        difDict[tType]+=[(dif,qData[i][0])]

def quality(dif):
    return 999-dif

for trform in tranformTypes:
    difDict[trform].sort()
difList=[]

bestDict={}
for i in range(len(qData)):#casNum
    bestDict[qData[i][0]]=[]

for i in range(len(qData)):
    tempList=[]
    for trform in tranformTypes:
        if bestDict[difDict[trform][i][1]]!="Done":
            bestDict[difDict[trform][i][1]]+=[difDict[trform][i][0]]
    for casNum in list(bestDict.keys()):
        if bestDict[casNum]!="Done":
            if len(bestDict[casNum])>=max(1,len(tranformTypes)-1):
                n=0
                for each in bestDict[casNum]:
                    n=max(n,each)
                tempList+=[(n,casNum)]
                bestDict[casNum]="Done"
    if tempList:
        tempList.sort()
        difList+=tempList
            
retString=""

#save list of compound differences to file
#f = open(os.path.join("output",'Ranked Differences.txt'), "w")
for i in range(len(difList)):
    #f.write('#'+str(i+1)+': '+qData[difList[i][1]][0]+'.pdf\n')
    
    #retString+=difList[i][1]+" "+str(difList[i][0])+"\n"
    retString+=difList[i][1]+" "
    
    #f.write("difference = "+ str(difList[i][0]) + '\n\n')
#f.close()

print(retString.strip())

#print("Done in",T.time()-startTime)
#print(tranformTypes)

sys.stdout.flush()
