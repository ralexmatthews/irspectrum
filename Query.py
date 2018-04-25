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
import sys
import sqlite3
import os
from IR_Functions import *
import multiprocessing as mp
from shutil import copyfile
#------------------------------------------------------------------------------

#---------------------------------Variables------------------------------------

#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------

#------------------------------------------------------------------------------

#----------------------------Multiprocessing functions-------------------------


def work(DataQ, ReturnQ, query, transformTypes):
    try:
        casNum, dataDict = DataQ.get()

        difDict = {}
        for tType in transformTypes:
            difDict[tType] = []

            dif=Compare(tType,dataDict[tType],query[tType])

            difDict[tType] += [(dif, casNum)]
        ReturnQ.put(difDict)
        return True
    except Exception as e:
        #uncomment to debug
        #'''
        print('\nERROR!:')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('%s' % e)
        print("\n"+str(exc_tb.tb_lineno)+" "+str(exc_obj)+" "+str(exc_tb),"\n")
        #'''
        return False


def worker(workerNo, JobsDoneQ, NofJobs, NofWorkers, ReturnQ, DataQ, query, transformTypes):
    # Worker loop
    working = True
    while working:
        jobNo = JobsDoneQ.get()
        message = work(DataQ, ReturnQ, query, transformTypes)
        if NofJobs-jobNo <= NofWorkers-1:
            working = False

#------------------------------------------------------------------------------

#---------------------------------Program Main---------------------------------
def formatQueryData(queryPath, transformTypes, filename):
    """ Open the source image """
    images = PullImages(queryPath)  # PullImages() from IR_Functions.py
    data = ReadGraph(images[0])  # ReadGraph() from IR_Functions.py
    
    copyfile(images[0], "public\\uploads\\" + filename)

    def timeStamp(f):
        return int(f.split('.')[0].split('_')[-1])
    
    currentTime=timeStamp(filename)
    holdTime=5*60*1000
    for each in [file for file in os.listdir("public\\uploads") if file.endswith(".jpg")]:
        try:
            if timeStamp(each)<currentTime-holdTime:
                os.remove("public\\uploads\\"+each)
        except:
            pass
    f.close()
    
    os.remove(images[0])  # Cleans up temp data from user's Query.
    if 'temp' in queryPath:
        os.remove(queryPath)

    #calculate each transformation
    queryDict={}
    #Cumulative() from IR_Functions.py
    queryDict=ConvertQuery(data,transformTypes)

    return queryDict
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def compareQueryToDB(formatedQueryData,transformTypes):

    # used to grab the total number of molecules
    conn = sqlite3.connect(os.path.realpath("IR.db"))
    sqlQ = "SELECT CAS_Num FROM IR_Info GROUP BY CAS_Num"
    cur = conn.cursor()
    cur.execute(sqlQ)
    qData = cur.fetchall()

    sqlQ = "SELECT CAS_Num,Type,Wavelength,Value FROM IR_Data"
    cur = conn.cursor()
    cur.execute(sqlQ)
    data = cur.fetchall()

    dataDict = {}

    for i in range(len(qData)):
        dataDict[qData[i][0]] = {}
        for tType in transformTypes:
            dataDict[qData[i][0]][tType] = []
    for i in range(len(data)):
        if 'raw'!=data[i][1]:
            dataDict[data[i][0]][data[i][1]]+=[data[i][2:]]
        else:
            for tType in transformTypes:
                if 'raw' in tType:
                    dataDict[data[i][0]][tType]+=[data[i][2:]]


    difDict={}
    for tType in transformTypes:
        difDict[tType]=[]
    
    CORES = mp.cpu_count()
    JobsDoneQ=mp.Queue()
    ReturnQ=mp.Queue()
    ReadRequestQ=mp.Queue()
    DataQ=mp.Queue()
    DataBuffer=CORES*2
    
    for i in range(len(qData)):
        JobsDoneQ.put(i+1)
        ReadRequestQ.put(1)
    for i in range(DataBuffer):
        DataQ.put((qData[i][0], dataDict[qData[i][0]]))
        ReadRequestQ.get()
        ReadRequestQ.put(0)

    p = {}
    for i in range(CORES):
        p[i] = mp.Process(target=worker,
                          args=[i, JobsDoneQ, len(qData), CORES, ReturnQ, DataQ, formatedQueryData, transformTypes])
        p[i].start()

    # Read returned data from workers, add new read reqests
    for i in range(DataBuffer, len(qData)+DataBuffer):
        retDict = ReturnQ.get()
        for tType in transformTypes:
            difDict[tType] += retDict[tType]
        if ReadRequestQ.get():
            DataQ.put((qData[i][0], dataDict[qData[i][0]]))

    for i in range(CORES):
        p[i].join()

    #sort compounds by difference. AddSortResults() from IR_Functions.py
    results=SmartSortResults(difDict,[a[0] for a in qData])[:min(20,len(qData))]
    retString=""

    # save list of compound differences to file
    for i in range(len(results)):
        retString+=results[i][1]+" "
        #retString+=results[i][1]+","+str(int(results[i][0]))+"\n"

    # Gives sorted list of Output to main.js
    print(retString.strip())

    sys.stdout.flush()
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == "__main__":
    
    f=open("public\\types.keys",'r')
    transformTypes=f.readlines()
    f.close()
    
    formatedQueryData = formatQueryData(sys.argv[1],transformTypes, sys.argv[2])

    compareQueryToDB(formatedQueryData,transformTypes)
#---------------------------------End of Program-------------------------------
