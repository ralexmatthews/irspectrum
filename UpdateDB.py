"""
Program: IRSpectrum.py
Programmed by: Josh Ellis, Josh Hollingsworth, Aaron Kruger, Alex Matthews, and
    Joseph Sneddon
Description: This program will recieve an IR Spectrograph of an unknown
    molecule and use our algorithm to compare that graph to a stored database of
    known molecules and their IR Spectrographs. This program will then return a
    list of the closest Spectrographs matches as determined by our algorithm.
UpdateDB.py: This part of the program imports all pdf files from */IR samples
    and updates the database (IR.db) with each new compound found.
"""
#---------------------------------Imports--------------------------------------
import sys
import sqlite3
import os
from PIL import Image
from shutil import copyfile
import multiprocessing as mp
import time
from IR_Functions import *
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------
def checkForDB():
    # if DB file somehow gets deleted re-create it
    if not os.path.exists("IR.db"):
        file = open('IR.db', 'w+')
        file.close()
    else:
        #os.remove("IR.db")
        pass

    sqlData = "CREATE TABLE IF NOT EXISTS `IR_Data` ( `CAS_Num` TEXT, `Type` TEXT, `Wavelength` NUMERIC, `Value` NUMERIC )"
    sqlInfo = "CREATE TABLE IF NOT EXISTS `IR_Info` ( `Spectrum_ID` TEXT, `CAS_Num` TEXT, `Formula` TEXT, `Compound_Name` TEXT, PRIMARY KEY(`Spectrum_ID`) )"

    conn = sqlite3.connect(os.path.realpath("IR.db"))
    cur = conn.cursor()
    tryWrite(sqlData, cur)
    tryWrite(sqlInfo, cur)
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

def tryWork(Jobs,transformTypes):
    try:
        file = Jobs.get(True,0)

        """ Open the source image """
        images = PullImages(file)

        fname = file.split("\\")[-1]
        casNum = fname.split(".")[0]

        """ is this file already in the database? """
        conn = sqlite3.connect(os.path.realpath("IR.db"))
        sqlQ = "SELECT CAS_Num FROM IR_Info WHERE CAS_Num='"+casNum+"'"
        sqlData = "SELECT CAS_Num FROM IR_Data WHERE CAS_Num='"+casNum+"'"
        sqlInfo = "INSERT INTO IR_Info(Spectrum_ID, CAS_Num, Formula, Compound_Name) VALUES (?, ?, ?, ?)"

        cur = conn.cursor()
        curData = conn.cursor()

        tryWrite(sqlQ, cur)
        tryWrite(sqlData, curData)

        qData = cur.fetchall()
        aData = curData.fetchall()

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
            tryWrite(sqlInfo, curr, dbvalues)
            tryCommit(conn)

            f=open("public\\info\\"+casNum+".json",'w')
            f.write(str(values).replace("'",'"'))
            f.close()
        else:
            os.remove(images[0])
            return casNum+" already in DB"

        data=ReadGraph(images[0])
        os.remove(images[0])

        #calculate each transformation
        transformDict={}
        for tType in transformTypes:
            transformDict[tType]=Convert(data,tType)

        sqlQ = "INSERT INTO IR_Data(CAS_Num, Type, Wavelength, Value) VALUES (?, ?, ?, ?)"
        #save each transformation to file
        for k in transformDict:
            d=[]
            for each in transformDict[k]:
                d+=[str(each[0])+','+str(each[1])]
                dbvalues = (casNum, k, each[0], each[1])
                currr = conn.cursor()
                tryWrite(sqlQ, currr, dbvalues)
                #save data

        tryCommit(conn)
        return casNum+" added to DB"




    except Exception as e:
        #uncomment to debug
        '''
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('%s' % e)
        print("\n"+str(exc_tb.tb_lineno)+" "+str(exc_obj)+" "+str(exc_tb))
        #'''
        return False

def worker(Jobs,workerNo,JobsDoneQ,NofJobs,transformTypes):
    working=True
    while working:
        message=tryWork(Jobs,transformTypes)
        if message:
            jobNo=JobsDoneQ.get()
            print("[Worker No. "+str(workerNo)+"] "+str(jobNo)+" of "+str(NofJobs)+" "+message)
        else:
            working=False
#------------------------------------------------------------------------------

#---------------------------------Program Main---------------------------------
if __name__ == "__main__":

    f=open("public\\types.keys",'r')
    transformTypes=f.readlines()
    f.close()

    #transformTypes=["cumulative.raw.10", "cumulative.raw.20", "cumulative.raw.30"]

    #Edit transformTypes to include only a single raw if other raw comparisons exist
    raws=[]
    for i in range(len(transformTypes)-1,-1,-1):
        if 'raw' in transformTypes[i]:
            raws+=[transformTypes.pop(i)]
    if len(raws)>0:
        transformTypes+=['raw']

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
        p[i] = mp.Process(target = worker, args=[Jobs,i,JobsDoneQ,len(filedir),transformTypes])
        p[i].start()
    for i in range(CORES):
        p[i].join()
    input("Done and Done "+str(time.time()-start))
#---------------------------------End of Program-------------------------------
