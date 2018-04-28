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

#---------------------------------Classes/Functions----------------------------
class FormatQueryData:
    def __new__(self, queryPath, comparisonTypes, filename):
        """
        Creates class object and initializes class variables, then returns a
        dictionary of the formated query data.
        """
        self.queryPath = queryPath
        self.comparisonTypes = comparisonTypes
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
        IR_Data = ReadGraph(images[0])  #ReadGraph() from IR_Functions.py

        copyfile(images[0], "public\\uploads\\" + self.filename)

        #Cleans up temp data from queries.
        self.cleanupQueryData(self, images)

        #Calculate each transformation. ConvertQuery() from IR_Functions.py
        queryDict=ConvertQuery(IR_Data,self.comparisonTypes)

        return queryDict
#------------------------------------------------------------------------------

#----------------------------Multiprocessing functions-------------------------
def work(DataQ, ReturnQ, query, comparisonTypes):
    try:
        casNum, dataDict = DataQ.get()

        difDict = {}
        for cType in comparisonTypes:
            difDict[cType] = []

            dif=Compare(cType,dataDict[cType],query[cType])

            difDict[cType] += [(dif, casNum)]
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
            comparisonTypes):
    # Worker loop
    working = True
    while working:
        jobNo = JobsDoneQ.get()
        message = work(DataQ, ReturnQ, query, comparisonTypes)
        if NofJobs-jobNo <= NofWorkers-1:
            working = False

def multiProcessController(formatedQueryData,comparisonTypes,IR_Info,dataDict,difDict):
    CORES = mp.cpu_count()
    JobsDoneQ=mp.Queue()
    ReturnQ=mp.Queue()
    ReadRequestQ=mp.Queue()
    DataQ=mp.Queue()
    DataBuffer=CORES*2

    for i in range(len(IR_Info)):
        JobsDoneQ.put(i+1)
        ReadRequestQ.put(1)
    for i in range(DataBuffer):
        DataQ.put((IR_Info[i][0], dataDict[IR_Info[i][0]]))
        ReadRequestQ.get()
        ReadRequestQ.put(0)

    p = {}
    for i in range(CORES):
        p[i] = mp.Process(target=worker,
                          args=[i, JobsDoneQ, len(IR_Info), CORES, ReturnQ, DataQ,
                                formatedQueryData, comparisonTypes])
        p[i].start()

    #Read returned data from workers, add new read reqests
    for i in range(DataBuffer, len(IR_Info)+DataBuffer):
        retDict = ReturnQ.get()
        for cType in comparisonTypes:
            difDict[cType] += retDict[cType]
        if ReadRequestQ.get():
            DataQ.put((IR_Info[i][0], dataDict[IR_Info[i][0]]))

    for i in range(CORES):
        p[i].join()
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def importDB():
    myIRDB = IRDB()
    IR_Info = myIRDB.searchIRDB("SELECT CAS_Num FROM IR_Info GROUP BY CAS_Num")
    IR_Data=myIRDB.searchIRDB("SELECT CAS_Num,Type,Wavelength,Value FROM IR_Data")

    return IR_Info, IR_Data

def generateDataDict(IR_Info, IR_Data, comparisonTypes):
    dataDict = {}
    for i in range(len(IR_Info)):
        dataDict[IR_Info[i][0]] = {}
        for cType in comparisonTypes:
            dataDict[IR_Info[i][0]][cType] = []
    for i in range(len(IR_Data)):
        if 'raw'!=IR_Data[i][1]:
            dataDict[IR_Data[i][0]][IR_Data[i][1]]+=[IR_Data[i][2:]]
        else:
            for cType in comparisonTypes:
                if 'raw' in cType:
                    dataDict[IR_Data[i][0]][cType]+=[IR_Data[i][2:]]
    return dataDict

def generateDifDict(comparisonTypes):
    difDict = {}
    for cType in comparisonTypes:
        difDict[cType]=[]
    return difDict

def compareQueryToDB(formatedQueryData,comparisonTypes):
    IR_Info, IR_Data = importDB()

    dataDict = generateDataDict(IR_Info, IR_Data, comparisonTypes)

    difDict = generateDifDict(comparisonTypes)

    multiProcessController(formatedQueryData,comparisonTypes,IR_Info,dataDict,difDict)

    #Sort compounds by difference. AddSortResults() from IR_Functions.py
    results=SmartSortResults(difDict,[a[0] for a in IR_Info])[:min(20,len(IR_Info))]
    retString=""

    #Save list of compound differences to file
    for i in range(len(results)):
        retString+=results[i][1]+" "
        #retString+=results[i][1]+","+str(int(results[i][0]))+"\n"

    #Gives sorted list of Output to main.js
    return retString.strip()
#------------------------------------------------------------------------------

#---------------------------------Program Main---------------------------------
def main(queryPath, filename):
    if __name__ == "__main__":

        comparisonTypes=ReadComparisonKeys()
        
        formatedQueryData = FormatQueryData(queryPath,comparisonTypes,filename)

        results = compareQueryToDB(formatedQueryData,comparisonTypes)
        print(results)

        sys.stdout.flush()
main(sys.argv[1], sys.argv[2])
#---------------------------------End of Program-------------------------------
