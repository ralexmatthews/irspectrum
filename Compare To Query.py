import sys
import os
from os import path
from PIL import Image, ImageTk
from math import log

#size of graph images
Width=866
Height=696

#list of all compounds
filedir=[file for file in os.listdir("IR samples") if file.endswith(".pdf")]

#list of total diffence for each compound
difList=[]

#only compare by peak for now
tranformTypes={"peak": (255,0,0), "basic": (0,255,0),"absD":(0,0,255)}
#tranformTypes={"peak": (255,0,0), "basic": (0,255,0)}
#tranformTypes={"absD":(0,0,255)}
#tranformTypes={"peak": (255,0,0)}
#tranformTypes={"basic": (0,255,0)}

Debug=False

if len(sys.argv)==1:
    target="query\\Query.pdf"
else:
    target=str(sys.argv[1]).strip()
    if "-debug" in sys.argv[2:]: Debug=True

try:
    for i in range(len(filedir)):

        difference=0
        for tType in tranformTypes:
            
            file1=os.path.join("data",filedir[i]+"."+tType)
            file2=target+"."+tType

            def str2Tuple(s):#convert strings to 2 element tuples (float,float)
                
                if s=='None':
                    return None
                
                x,y =s. split(',')
                return ( float(x) , float(y) )

            #read data for the compound
            f = open(file1, "r")
            lines=f.readlines()
            transformation1=[str2Tuple(s.strip()) for s in lines]

            #read data for the query
            f = open(file2, "r")
            lines=f.readlines()
            transformation2=[str2Tuple(s.strip()) for s in lines]

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

            if Debug:
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

            dif=0
            #total the differences between the compound and the query
            # also draw an image to show this comparison
            for a in range(min(len(transformation1),len(transformation2))):
                dif+=abs(transformation1[a][1]-transformation2[a][1])
                if Debug:
                    y1=min(deverty(transformation1[a][1]),deverty(transformation2[a][1]))
                    y2=max(deverty(transformation1[a][1]),deverty(transformation2[a][1]))

                    x=devertx(transformation1[a][0])
                    for y in range(y1,y2+1):
                        addPix(x,y,tranformTypes[tType])

            if Debug:
                #save image
                img = Image.new('RGB', (Width, Height))
                img.putdata(graph)
                img.save(os.path.join("output",file1.split(".")[0]+tType+'.comp.png'))

            difference+=dif

        difList+=[(difference,i)]

    #sort compounds by difference
    difList.sort()

    retString=""


    #build list of compounds sorted by differences
    for i in range(len(difList)):
        retString+=filedir[difList[i][1]][:-4]+" "

    if Debug:
        f = open(os.path.join("output",'Ranked Differences.txt'), "w")
        f.write(retString.strip())
        f.close()

    print(retString.strip())

    sys.stdout.flush()
    
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    f = open('err.txt', "w")
    f.write('%s' % e)
    f.write("\n"+str(exc_tb.tb_lineno))
    f.close()

