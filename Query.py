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
import PyPDF2  # TODO are we using pyPDF2 in Query.py???
import time
import sys
import sqlite3
import warnings  # TODO are we using warnings in Query.py???
import os
from os import path  # TODO do we need both import os and from os import path???
from PIL import Image, ImageTk  # TODO are we using ImageTK in Query.py???
from math import log  # TODO are we still using log in Query.py???
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

            # total the differences between the compound and the query also draw
            # an image to show this comparison. Compare() from IR_Functions.py
            dif = Compare(tType, dataDict[tType], query[tType])

            difDict[tType] += [(dif, casNum)]
        ReturnQ.put(difDict)
        return True
    except Exception as e:
        # uncomment to debug
        #'''
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('%s' % e)
        print("\n"+str(exc_tb.tb_lineno)+" "+str(exc_obj)+" "+str(exc_tb))
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


def formatQueryData(queryPath, filename):
    """ Open the source image """
    images = PullImages(queryPath)  # PullImages() from IR_Functions.py
    data = ReadGraph(images[0])  # ReadGraph() from IR_Functions.py
    copyfile(images[0], "public\\uploads\\" + filename)
    os.remove(images[0])  # Cleans up temp data from user's Query.
    os.remove(queryPath)

    # calculate each transformation
    transformDict = {}
    # Cumulative() from IR_Functions.py
    # TODO change Cumulative() to accept data instead of one element at a time?
    transformDict["cumulative"] = Cumulative([(e[0], e[2]) for e in data])

    return transformDict
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------


def compareQueryToDB(formatedQueryData):
    # only compare by cumulative for now
    transformTypes = ["cumulative"]

    # used to grab the total number of molecules
    conn = sqlite3.connect(os.path.realpath("IR.db"))
    sqlQ = "SELECT CAS_Num FROM IR_Raw GROUP BY CAS_Num"
    cur = conn.cursor()
    cur.execute(sqlQ)
    qData = cur.fetchall()

    sqlQ = "SELECT CAS_Num,Type,Wavelength,Value FROM IR_JoshEllisAlgorithm"
    cur = conn.cursor()
    cur.execute(sqlQ)
    data = cur.fetchall()

    dataDict = {}

    for i in range(len(qData)):
        dataDict[qData[i][0]] = {}
        for tType in transformTypes:
            dataDict[qData[i][0]][tType] = []
    for i in range(len(data)):
        dataDict[data[i][0]][data[i][1]] += [data[i][2:]]

    difDict = {}
    for tType in formatedQueryData:
        difDict[tType] = []

    CORES = mp.cpu_count()
    JobsDoneQ = mp.Queue()
    ReturnQ = mp.Queue()
    ReadRequestQ = mp.Queue()
    DataQ = mp.Queue()
    DataBuffer = CORES*2
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

    # sort compounds by difference. AddSortResults() from IR_Functions.py
    results = AddSortResults(difDict, [a[0] for a in qData])[:200]
    retString = ""

    # save list of compound differences to file
    for i in range(len(results)):
        retString += results[i][1]+" "

    # Gives sorted list of Output to main.js
    print(retString.strip())

    sys.stdout.flush()
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
if __name__ == "__main__":
    formatedQueryData = formatQueryData(sys.argv[1], sys.argv[2])

    compareQueryToDB(formatedQueryData)
#---------------------------------End of Program-------------------------------
