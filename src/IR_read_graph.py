from PIL import Image, ImageTk
import sys

'''
Open the source image
Crop the image
Save the cropped image
'''

#open image from user's commandline argument
img = Image.open(sys.argv[1])
imgdata=list(img.getdata())#the pixels from the image

#this with and height seems to be standard for all IR samples
Width=1024
Height=768

#the area of each image that we want (the actual graph)
        #(left,right,top,bottom)
targetRect=(113,978,29,724)

#copies pixels from the source image within the targetRect
def cropRect(source,rect):
    left,right,top,bottom=rect
    newImg=[]
    #copy specified pixels
    for y in range(top,bottom+1):
        for x in range(left,right+1):
            newImg+=[source[y*Width+x]]
    return newImg

#the graph cut out of the larger image
graph=cropRect(imgdata,targetRect)

#width and height of cropped graph
Width=targetRect[1]-targetRect[0]+1
Height=targetRect[3]-targetRect[2]+1

#save the cropped graph image
img = Image.new('RGB', (Width, Height))
img.putdata(graph)
img.save('graph.png')

'''
Create data list by reading pixels from graph
    -each entry in data is the range over wich each
     column has black pixels
Save data to file
'''

def pix(x,y):#checks if the pixel at x,y is black
    r,g,b=graph[y*Width+x]
    if r+g+b>=100:
        return False#not black
    else:
        return True#black

data=[]#to be filled with values from graph

#For each x get the y range over which the graph has black pixels
# or None if the graph is empty at that x value
for x in range(0,Width):
    data+=[None]
    foundPix=False#have you found a pixel while looping through the column
    for y in range(0,Height):
        p=pix(x,y)#is the pixel black
        if p and not foundPix:
            #record the first black pixels y value
            foundPix=True
            maxVal=y
        elif not p and foundPix:
            #record the last black pixels y value
            minVal=y
            data[-1]=(minVal,maxVal)#write these values to data
            break#next x

#save data to file
f = open("data.txt", "w")
for element in data:
    f.write(str(element) + '\n')
f.close()

print('done')
            
