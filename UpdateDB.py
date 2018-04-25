"""
This can be ran from the command line with the pdf file you wish to extract from
as an argument, it will save the image in the same directory you are in.
"""
#---------------------------------Imports--------------------------------------
import PyPDF2 #TODO is this used in UpdateDB.py???
import sys
import sqlite3
import warnings #TODO are we still using warnings in UpdateDB.py???
import os
from os import path #TODO do we need both import os and from os import path???
from PIL import Image, ImageTk
from math import log #TODO I don't think we use this anymore.
from shutil import copyfile
import multiprocessing as mp
import time
from IR_Functions import *
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------
def tryCommit(conn):
    trying=True
    while trying:
        try:
            conn.commit()
            trying=False
        except:
            pass

def tryWrite(sqlQ,cur,dbvalues=None):
    trying=True
    while trying:
        try:
            if dbvalues:
                cur.execute(sqlQ, dbvalues)
            else:
                cur.execute(sqlQ)
            trying=False
        except:
            pass

def tryWork(Jobs):
    try:
        file = Jobs.get(True,0)

        """ Open the source image """
        images = PullImages(file)

        addToDB = False

        fname = file.split("\\")[-1]
        casNum = fname.split(".")[0]

        """ is this file already in the database? """
        conn = sqlite3.connect(os.path.realpath("IR.db"))
        sqlQ = "SELECT CAS_Num FROM IR_Raw WHERE CAS_Num='"+casNum+"'"
        cur = conn.cursor()
        tryWrite(sqlQ,cur)
        qData = cur.fetchall()

        """ if not in the database set the flag to add it """
        if len(qData)==0:
            addToDB = True
            
            copyfile(images[0],"public\\images\\"+casNum+".jpg")
            
            structure=PullStructure(file)[0]
            CleanStructure(structure)
            copyfile(structure,"public\\info\\"+structure.split("\\")[-1])
            os.remove(structure)
            
            values=PullText(file)
            f=open("public\\info\\"+casNum+".json",'w')
            f.write(str(values).replace("'",'"'))
            f.close()
        else:
            os.remove(images[0])
            return casNum+" already in"

        data=ReadGraph(images[0])
        os.remove(images[0])

        #save data
        sqlQ = "INSERT INTO IR_Raw(CAS_Num, Wavelength, x_min, x_max) VALUES (?, ?, ?, ?)"

        for element in data:
            if addToDB:
                dbvalues = (casNum, element[0], element[1], element[2])
                cur = conn.cursor()
                tryWrite(sqlQ,cur, dbvalues)
        if addToDB:
            tryCommit(conn)

        #calculate each transformation
        transformDict={}
        transformDict["cumulative"]=Cumulative([(e[0],e[2]) for e in data])

        sqlQ = "INSERT INTO IR_JoshEllisAlgorithm(CAS_Num, Type, Wavelength, Value) VALUES (?, ?, ?, ?)"
        #save each transformation to file
        for k in transformDict:
            d=[]
            for each in transformDict[k]:
                d+=[str(each[0])+','+str(each[1])]
                if addToDB: # add stuff to DB if doesn't exist
                    dbvalues = (casNum, k, each[0], each[1])
                    cur = conn.cursor()
                    tryWrite(sqlQ,cur, dbvalues)
                #save data

        if addToDB:
            tryCommit(conn)
            addToDB = False
            return casNum+" added to DB"
        else:
            return casNum+" already in DB"



    except Exception as e:
        #uncomment to debug
        '''
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('%s' % e)
        print("\n"+str(exc_tb.tb_lineno)+" "+str(exc_obj)+" "+str(exc_tb))
        #'''
        return False

def worker(Jobs,workerNo,JobsDoneQ,NofJobs):
    working=True
    while working:
        message=tryWork(Jobs)
        if message:
            jobNo=JobsDoneQ.get()
            print("[Worker No. "+str(workerNo)+"] "+str(jobNo)+" of "+str(NofJobs)+" "+message)
        else:
            working=False
#------------------------------------------------------------------------------

#---------------------------------Program Main---------------------------------
if __name__ == "__main__":

    filedir=[os.path.join("IR samples",file) for file in os.listdir("IR samples") if file.endswith(".pdf")]

    Jobs=mp.Queue()
    JobsDoneQ=mp.Queue()
    for i in range(len(filedir)):
        Jobs.put(filedir[i])
        JobsDoneQ.put(i+1)

    CORES = mp.cpu_count()
    p={}
    print("Starting")
    start=time.time()
    for i in range(CORES):
        p[i] = mp.Process(target = worker, args=[Jobs,i,JobsDoneQ,len(filedir)])
        p[i].start()
    for i in range(CORES):
        p[i].join()
    input("Done and Done "+str(time.time()-start))
#---------------------------------End of Program-------------------------------
