import sys
import os
from os import path
from PIL import Image, ImageTk
from math import log

#size of graph images
Width=866
Height=696

#list of all compounds
filedir=[file for file in os.listdir("IR samples") if file.endswith(".pdf") and file!="Query1.pdf"]

#list of total diffence for each compound
difList=[]

#only compare by peak for now
tranformTypes=["peak"]#"basic","absD",

for i in range(len(filedir)):
    print(str(i+1),"of",len(filedir))

    for tType in tranformTypes:
        
        file1=filedir[i]+"."+tType
        file2="Query1.pdf."+tType

        def str2Tuple(s):#convert strings to 2 element tuples (float,float)
            
            if s=='None':
                return None
            
            x,y =s. split(',')
            return ( float(x) , float(y) )

        #read data for the compound
        f = open("data\\"+file1, "r")
        lines=f.readlines()
        transformation1=[str2Tuple(s.strip()) for s in lines]

        #read data for the query
        f = open("data\\"+file2, "r")
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

        graph=[]
        #create graph as white blank image
        for x in range(Width):
            for y in range(Height):
                graph+=[(255,255,255)]

        #draw a pixel
        def drawPix(x,y,c):
            graph[int(y*Width+x)]=c

        dif=0
        #total the differences between the compound and the query
        # also draw an image to show this comparison
        for a in range(min(len(transformation1),len(transformation2))):
            dif+=abs(transformation1[a][1]-transformation2[a][1])
            y1=min(deverty(transformation1[a][1]),deverty(transformation2[a][1]))
            y2=max(deverty(transformation1[a][1]),deverty(transformation2[a][1]))

            x=devertx(transformation1[a][0])
            for y in range(y1,y2+1):
                drawPix(x,y,(255,0,0))

        #save image
        img = Image.new('RGB', (Width, Height))
        img.putdata(graph)
        img.save("output\\"+file1.split(".")[0]+tType+'.comp.png')
        
        '''
        f = open("output\\"+file1.split(".")[0]+tType+'.comp.txt', "w")
        f.write(file1+" x "+file2 + '\n')
        f.write("difference = "+ str(dif) + '\n')
        f.close()
        '''
        
        difList+=[(dif,i)]

#sort compounds by difference
difList.sort()

#save list of compound differences to file
f = open("output\\"+'Ranked Differences.txt', "w")
for i in range(len(difList)):
    f.write('#'+str(i+1)+': '+filedir[difList[i][1]]+'\n')
    f.write("difference = "+ str(difList[i][0]) + '\n\n')
f.close()

print("done")
