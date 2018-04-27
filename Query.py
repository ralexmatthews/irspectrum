"""
Program: IRSpectrum.py
Programmed by: Josh Ellis, Josh Hollingsworth, Aaron Kruger, Alex Matthews, and
    Joseph Sneddon
Description: This program will recieve an IR Spectrograph of an unknown
    molecule and use our algorithm to compare that graph to a stored database of
    known molecules and their IR Spectrographs. This program will then return a
    list of the closest Spectrographs matches as determined by our algorithm.
Query.py: This part of the program recieves the file location of a query IR
    Spectrograph downloaded by main.js. formatQueryData() then formats the query
    data and returns a dictionary, queryDict, of the formated query data.
    compareQueryToDB() then takes that dictionary and compares it against all of
    the IR spectrographs imported from our IR spectrum database (IR.db).
    compareQueryToDB() then sends a string back to main.js of the closest IR
    spectrographs found in the IR.db.
"""
#---------------------------------Imports--------------------------------------
import sys
import os
from IR_Functions import *
import multiprocessing as mp
from shutil import copyfile
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

def worker(workerNo, JobsDoneQ, NofJobs, NofWorkers, ReturnQ, DataQ, query,
            transformTypes):
    # Worker loop
    working = True
    while working:
        jobNo = JobsDoneQ.get()
        message = work(DataQ, ReturnQ, query, transformTypes)
        if NofJobs-jobNo <= NofWorkers-1:
            working = False
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------
class FormateQueryData:
    def __new__(self, queryPath, transformTypes, filename):
        """
        Creates class object and initializes class variables, then returns a
        dictionary of the formated query data.
        """
        self.queryPath = queryPath
        self.transformTypes = transformTypes
        self.filename = filename

        return self.formatQueryData(self)

    def timeStamp(self, f):
        return int(f.split('.')[0].split('_')[-1])

    def cleanupQueryData(self, images):
        """Removes all generated query data that is more than 5 min old."""
        currentTime = self.timeStamp(self, self.filename)
        holdTime=5*60*1000
        for each in [file for file in os.listdir("public\\uploads")
                        if file.endswith(".jpg")]:
            try:
                if self.timeStamp(self, each)<currentTime-holdTime:
                    os.remove("public\\uploads\\"+each)
            except:
                pass

        #Deletes the temp file downloaded by main.js
        os.remove(images[0])
        if 'temp' in self.queryPath:
            os.remove(self.queryPath)

    def formatQueryData(self):
        #Open the source image
        images = PullImages(self.queryPath)  #PullImages() from IR_Functions.py
        data = ReadGraph(images[0])  #ReadGraph() from IR_Functions.py

        copyfile(images[0], "public\\uploads\\" + self.filename)

        #Cleans up temp data from queries.
        self.cleanupQueryData(self, images)

        #Calculate each transformation. ConvertQuery() from IR_Functions.py
        queryDict=ConvertQuery(data,self.transformTypes)

        return queryDict
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def importDB():

    myIRDB = IRDB()
    qData = myIRDB.searchIRDB("SELECT CAS_Num FROM IR_Info GROUP BY CAS_Num")
    data=myIRDB.searchIRDB("SELECT CAS_Num,Type,Wavelength,Value FROM IR_Data")

    return qData, data

def generateDataDict(qData, data, transformTypes):
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
    return dataDict

def generateDifDict(transformTypes):
    difDict = {}
    for tType in transformTypes:
        difDict[tType]=[]
    return difDict

def compareQueryToDB(formatedQueryData,transformTypes):
    qData, data = importDB()

    dataDict = generateDataDict(qData, data, transformTypes)

    difDict = generateDifDict(transformTypes)

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
                          args=[i, JobsDoneQ, len(qData), CORES, ReturnQ, DataQ,
                                formatedQueryData, transformTypes])
        p[i].start()

    #Read returned data from workers, add new read reqests
    for i in range(DataBuffer, len(qData)+DataBuffer):
        retDict = ReturnQ.get()
        for tType in transformTypes:
            difDict[tType] += retDict[tType]
        if ReadRequestQ.get():
            DataQ.put((qData[i][0], dataDict[qData[i][0]]))

    for i in range(CORES):
        p[i].join()

    #Sort compounds by difference. AddSortResults() from IR_Functions.py
    results=SmartSortResults(difDict,[a[0] for a in qData])[:min(20,len(qData))]
    retString=""

    #Save list of compound differences to file
    for i in range(len(results)):
        retString+=results[i][1]+" "
        #retString+=results[i][1]+","+str(int(results[i][0]))+"\n"

    #Gives sorted list of Output to main.js
    #print(retString.strip())
    return retString.strip()

    sys.stdout.flush()
#------------------------------------------------------------------------------

#---------------------------------Program Main---------------------------------
def main(queryPath, filename):
    if __name__ == "__main__":

        f=open("public\\types.keys",'r')
        transformTypes=f.readlines()
        f.close()
        formatedQueryData = FormateQueryData(queryPath, transformTypes, filename)
        #formatedQueryData = query.formatQueryData()

        results = compareQueryToDB(formatedQueryData,transformTypes)
        print(results)

main(sys.argv[1], sys.argv[2])
#---------------------------------End of Program-------------------------------
