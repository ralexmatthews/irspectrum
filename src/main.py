from tkinter import *
from tkinter import filedialog
import os
import PyPDF2
from PIL import Image, ImageTk
import warnings
import ntpath
warnings.filterwarnings("ignore")

# this is for testing git
class IRSpectrumMain(Frame):
    '''This is the main menu class of the tkinter program. It will layout the
    main GUI and contain most of the functions we are going to need'''

    def __init__(self, parent):
        '''This is the main initialization, where we set up the layout setup 
        most of what we need'''

        Frame.__init__(self, parent)

        # main setup
        self.master.title("IR Spectrum Recognizer")
        self.grid()
        self.osPath = os.path.realpath(__file__)

        # set window to maximized
        w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        self.master.wm_state('zoomed')

        # set up rows and columns
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_columnconfigure(3, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_rowconfigure(3, weight=1)

        # setup buttons and gizmos
        # variables
        self.imagePath = StringVar()

        # buttons
        self.browseButton = Button(self, text='Search', command=self._openFiles, height=3, width=8)
        self.confirmButton = Button(self, text='Confirm', command=self._confirm)

        # photo stuff
        # I put in some filler stuff here so that I could format the pictures before the graph was implemented
        self.image = PhotoImage(file=os.path.abspath(os.path.join
                                                     (self.osPath, '..', '..', 'utilities', 'placeholder.png')))
        self.image1 = Image.open(os.path.abspath(os.path.join
                                                     (self.osPath, '..', '..', 'utilities', 'black.jpg')))
        self.image2 = Image.open(os.path.abspath(os.path.join
                                                     (self.osPath, '..', '..', 'utilities', 'black.jpg')))
        self.image3 = Image.open(os.path.abspath(os.path.join
                                                     (self.osPath, '..', '..', 'utilities', 'black.jpg')))
        self.image4 = Image.open(os.path.abspath(os.path.join
                                                     (self.osPath, '..', '..', 'utilities', 'black.jpg')))
        self.image1 = self.image1.resize((250, 175), Image.ANTIALIAS)
        self.image2 = self.image2.resize((250, 175), Image.ANTIALIAS)
        self.image3 = self.image3.resize((250, 175), Image.ANTIALIAS)
        self.image4 = self.image4.resize((250, 175), Image.ANTIALIAS)
        self.winner1 = ImageTk.PhotoImage(image=self.image1)
        self.winner2 = ImageTk.PhotoImage(image=self.image2)
        self.winner3 = ImageTk.PhotoImage(image=self.image3)
        self.winner4 = ImageTk.PhotoImage(image=self.image4)
        self.winnerImage1 = Label(image=self.winner1)
        self.winnerImage2 = Label(image=self.winner2)
        self.winnerImage3 = Label(image=self.winner3)
        self.winnerImage4 = Label(image=self.winner4)
        self.winnerImage1.grid(row=0, column=3)
        self.winnerImage2.grid(row=1, column=3)
        self.winnerImage3.grid(row=2, column=3)
        self.winnerImage4.grid(row=3, column=3)

        # labels
        self.imageLabel = Label(image=self.image)

        # text fields
        self.pathEntry = Entry(self, textvariable=self.imagePath, justify=LEFT, font='Helvetica 18', width=50)

        # placement
        self.pathEntry.grid(row=0, column=0, columnspan=2, sticky=N+E+S+W)
        self.browseButton.grid(row=0, column=2)
        self.confirmButton.grid(row=1, column=0, columnspan=2, sticky=N+S+E+W)
        self.imageLabel.grid(row=2, column=0, columnspan=2, rowspan=2, sticky=N+S+E+W)

    def _openFiles(self):
        '''This function will be used by the browse button to allow the user
        to search their files to open the IR Spectrum Analysis'''

        # get file user wants to use and set to self.imagePath
        path = filedialog.askopenfilename()
        self.imagePath.set(path)

        # if its a pdf, convert it and display it
        if path[-3:] == 'pdf':
            converter(path)
            self.otherPath = os.path.abspath(os.path.join(self.osPath, '..', '..', 'tempPics')) + '\\' \
                             + ntpath.basename(path)[:-4] + '.jpg'
            self.customImage = Image.open(self.otherPath)
            self.customImage = self.customImage.resize((600, 450), Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(self.customImage)
            self.imageLabel = Label(image=self.image)
            self.imageLabel.grid(row=2, column=0, columnspan=2, rowspan=2, sticky=N + S + E + W)

    def _confirm(self):
        '''This function will be used by the confirm button and will open
        up the next page to show the spectrum analysis'''

        # if they choose a valid picture, compare them
        if self.otherPath[-3:] == 'jpg' or self.otherPath[-3:] == 'png':

            # get original picture that user selected
            original = IR_read_graph(self.otherPath)

            # set up arrays needed for comparison
            compare = []
            differences = []

            # get the directory of precreated jpegs and set filenames to jpegs[]
            jpegs = os.listdir(os.path.abspath(os.path.join(self.osPath, '..', '..', 'IR jpegs')))

            # set the full path of every jpeg to compare[]
            for file in jpegs:
                compare.append(IR_read_graph(os.path.abspath(os.path.join(self.osPath, '..', '..', 'IR jpegs')) + '\\'
                                             + file))

            # --meat and potatoes-- this is the part that assigns a value to how similar the spectrums are
            # basically just adds up all the differences in pixels, lower score is more similar
            for molecule in compare:
                sum = 0
                for x in range(len(molecule)):
                    if molecule[x] and original[x]:
                        sum += abs(molecule[x][1] - original[x][1])

                differences.append(sum)

            # set up an original list to we can index where the values came from when we sort differences[]
            originalList = []
            for value in differences:
                originalList.append(value)

            # sort differences low to high
            differences.sort()

            # winners will hold the paths to the top 4 matches
            winners = []
            for x in range(4):
                for y in range(len(originalList)):
                    if differences[x] == originalList[y]:
                        winners.append(jpegs[y])
                        break

            # display the 4 winning pictures
            jpegsPath = os.path.abspath(os.path.join(self.osPath, '..', '..', 'IR jpegs'))
            self.image1 = Image.open(jpegsPath + '\\' + winners[0])
            self.image2 = Image.open(jpegsPath + '\\' + winners[1])
            self.image3 = Image.open(jpegsPath + '\\' + winners[2])
            self.image4 = Image.open(jpegsPath + '\\' + winners[3])
            self.image1 = self.image1.resize((250, 175), Image.ANTIALIAS)
            self.image2 = self.image2.resize((250, 175), Image.ANTIALIAS)
            self.image3 = self.image3.resize((250, 175), Image.ANTIALIAS)
            self.image4 = self.image4.resize((250, 175), Image.ANTIALIAS)
            self.winner1 = ImageTk.PhotoImage(image=self.image1)
            self.winner2 = ImageTk.PhotoImage(image=self.image2)
            self.winner3 = ImageTk.PhotoImage(image=self.image3)
            self.winner4 = ImageTk.PhotoImage(image=self.image4)
            self.winnerImage1 = Label(image=self.winner1)
            self.winnerImage2 = Label(image=self.winner2)
            self.winnerImage3 = Label(image=self.winner3)
            self.winnerImage4 = Label(image=self.winner4)
            self.winnerImage1.grid(row=0, column=3)
            self.winnerImage2.grid(row=1, column=3)
            self.winnerImage3.grid(row=2, column=3)
            self.winnerImage4.grid(row=3, column=3)




'''-----------Joshua Ellis's IR_read_graph.py-----------------------------'''


def IR_read_graph(file):
    # open image from user's commandline argument
    img = Image.open(file)
    imgdata = list(img.getdata())  # the pixels from the image

    # the area of each image that we want (the actual graph)
    # (left,right,top,bottom)
    targetRect = (113, 978, 29, 724)

    Width = 1024
    Height = 768

    # the graph cut out of the larger image
    graph = cropRect(imgdata, targetRect, Width)

    # width and height of cropped graph
    Width = targetRect[1] - targetRect[0] + 1
    Height = targetRect[3] - targetRect[2] + 1

    # save the cropped graph image
    img = Image.new('RGB', (Width, Height))
    img.putdata(graph)
    img.save(os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', 'tempPics')) + '\\' + 'graph.png')

    '''
    Create data list by reading pixels from graph
        -each entry in data is the range over wich each
         column has black pixels
    Save data to file
    '''



    data = []  # to be filled with values from graph

    # For each x get the y range over which the graph has black pixels
    # or None if the graph is empty at that x value
    for x in range(0, Width):
        data += [None]
        foundPix = False  # have you found a pixel while looping through the column
        for y in range(0, Height):
            p = pix(x, y, graph, Width)  # is the pixel black
            if p and not foundPix:
                # record the first black pixels y value
                foundPix = True
                maxVal = y
            elif not p and foundPix:
                # record the last black pixels y value
                minVal = y
                data[-1] = (minVal, maxVal)  # write these values to data
                break  # next x

    # save data to file
    # f = open("data.txt", "w")
    # for element in data:
    #     f.write(str(element) + '\n')
    # f.close()

    # print('done')
    return data


# copies pixels from the source image within the targetRect
def cropRect(source, rect, Width):

    left, right, top, bottom = rect
    newImg = []
    # copy specified pixels
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            newImg += [source[y * Width + x]]
    return newImg


def pix(x, y, graph, Width):  # checks if the pixel at x,y is black
    r, g, b = graph[y * Width + x]
    if r + g + b >= 100:
        return False  # not black
    else:
        return True  # black

'''-----------End Joshua Ellis's IR_read_graph.py-------------------------'''
'''--------------Aaron Kruger's jpegExtract.py----------------------------'''

number = 0


# helper function for conveter
def recurse(page, xObject, inputFile):
    global number

    xObject = xObject['/Resources']['/XObject'].getObject()

    for obj in xObject:

        if xObject[obj]['/Subtype'] == '/Image':
            size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
            data = xObject[obj]._data
            if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                mode = "RGB"
            else:
                mode = "P"

            osPath = os.path.realpath(__file__)
            imagename = os.path.abspath(os.path.join(osPath, '..', '..', 'tempPics')) + '\\' \
                        + ntpath.basename(inputFile)[:-4]

            if xObject[obj]['/Filter'] == '/FlateDecode':
                img = Image.frombytes(mode, size, data)
                img.save(imagename + ".png")
                number += 1
            elif xObject[obj]['/Filter'] == '/DCTDecode':
                img = open(imagename + ".jpg", "wb")
                img.write(data)
                img.close()
                number += 1
            elif xObject[obj]['/Filter'] == '/JPXDecode':
                img = open(imagename + ".jp2", "wb")
                img.write(data)
                img.close()
                number += 1
        else:
            recurse(page, xObject[obj])


# saves the input pdf as a jpg file in tempPics
def converter(inputFile):

    file = PyPDF2.PdfFileReader(open(inputFile, "rb"))

    page0 = file.getPage(0)

    p = 1
    recurse(p, page0, inputFile)

'''----------End Aaron Kruger's jpegExtract.py----------------------------'''

def main():
    root = Tk()
    main = IRSpectrumMain(root)
    main.mainloop()

main()