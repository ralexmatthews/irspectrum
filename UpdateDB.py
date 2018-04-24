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
def checkForDB() :
    # if DB file somehow gets deleted re-create it
    if not os.path.exists("IR.db"):
        file = open('IR.db', 'w+')
        file.close()

    sqlRAW = "CREATE TABLE IF NOT EXISTS `IR_Raw` ( `CAS_Num` TEXT, `Wavelength` NUMERIC, `x_min` NUMERIC, `x_max` NUMERIC )"
    sqlALG = "CREATE TABLE IF NOT EXISTS `IR_JoshEllisAlgorithm` ( `CAS_Num` TEXT, `Type` TEXT, `Wavelength` NUMERIC, `Value` NUMERIC )"
    sqlCOMP = "CREATE TABLE IF NOT EXISTS `IR_Compounds` ( `Spectrum_ID` TEXT, `CAS_Num` TEXT, `Formula` TEXT, `Compound_Name` TEXT, PRIMARY KEY(`Spectrum_ID`) )"

    conn = sqlite3.connect(os.path.realpath("IR.db"))
    cur = conn.cursor()
    tryWrite(sqlRAW, cur)
    tryWrite(sqlALG, cur)
    tryWrite(sqlCOMP, cur)
    tryCommit(conn)

def tryCommit(conn):
    trying=True
    while trying:
        try:
            conn.commit()
            trying=False
        except Exception as e:
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
        except Exception as e:
            pass

def tryWork(Jobs):
    try:
        file = Jobs.get(True,0)

        """ Open the source image """
        images = PullImages(file)

        addToDB = False
        addToDBAlg = False

        fname = file.split("\\")[-1]
        casNum = fname.split(".")[0]

        """ is this file already in the database? """
        conn = sqlite3.connect(os.path.realpath("IR.db"))
        sqlQ = "SELECT CAS_Num FROM IR_Compounds WHERE CAS_Num='"+casNum+"'"
        sqlRaw = "SELECT CAS_Num FROM IR_Raw WHERE CAS_Num='"+casNum+"'"
        sqlAlg = "SELECT CAS_Num FROM IR_JoshEllisAlgorithm WHERE CAS_Num='"+casNum+"'"
        sqlCompounds = "INSERT INTO IR_Compounds(Spectrum_ID, CAS_Num, Formula, Compound_Name) VALUES (?, ?, ?, ?)"

        cur = conn.cursor()
        curRaw = conn.cursor()
        curAlg = conn.cursor()

        tryWrite(sqlQ, cur)
        tryWrite(sqlRaw, curRaw)
        tryWrite(sqlAlg, curAlg)
        
        qData = cur.fetchall()
        rData = curRaw.fetchall()
        aData = curAlg.fetchall()

        if len(rData)==0:
            addToDB = True
        if len(aData)==0:
            addToDBAlg = True

        """ if not in the database set the flag to add it """
        if len(qData)==0: 
                            
            copyfile(images[0],"public\\images\\"+casNum+".jpg")
            
            structure=PullStructure(file)[0]
            CleanStructure(structure)
            copyfile(structure,"public\\info\\"+structure.split("\\")[-1])
            os.remove(structure)
            
            values=PullText(file)
            #Save compound data into the database
            dbvalues = (list(values.values())[0], casNum, list(values.values())[2], list(values.values())[3])
            
            curr = conn.cursor()
            tryWrite(sqlCompounds, curr, dbvalues)
            tryCommit(conn)
            
            f=open("public\\info\\"+casNum+".json",'w')
            f.write(str(values).replace("'",'"'))
            f.close()

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
                if addToDBAlg: # add stuff to DB if doesn't exist
                    dbvalues = (casNum, k, each[0], each[1])
                    currr = conn.cursor()
                    tryWrite(sqlQ, currr, dbvalues)
                #save data

        if addToDBAlg or addToDB:
            tryCommit(conn)
            addToDB = False
            addToDBAlg = False
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

    checkForDB()
    
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
