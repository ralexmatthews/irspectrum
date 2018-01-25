from tkinter import *
from tkinter import filedialog
import os


# def digitize(image):
#     '''This function takes the path of an image and returns a list
#     of the graph information. It goes pixel by pixel starting at
#     [516, 1773] and ending at [2397, 1773] and gives the height of
#     the graph at that point on a scale of 0-1'''
#
#     # array to store values of graph height
#     digitized = []
#
#     # set up opening image
#     im = Image.open(image)
#     pix = im.load()
#
#     # go across the line at y = 1773 and get the height
#     for x in range(516, 2397):
#         y = 1773
#         while True:
#             if not pix[x, y][0] > 200:
#                 digitized.append((1773 - y)/1517)
#                 break
#             y -= 1
#
#     return digitized

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
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)

        # setup buttons and gizmos
        # variables
        self.imagePath = StringVar()

        # buttons
        self.browseButton = Button(self, text='Search', command=self._openFiles, height=3, width=15)
        self.confirmButton = Button(self, text='Confirm', command=self._confirm)

        # photo
        self.image = PhotoImage(file=os.path.abspath(os.path.join(self.osPath, '..', '..', 'utilities', 'placeholder.png')))

        # labels
        self.imageLabel = Label(image=self.image)

        # text fields
        self.pathEntry = Entry(self, textvariable=self.imagePath, justify=LEFT, font='Helvetica 18', width=50)

        # placement
        self.pathEntry.grid(row=0, column=0, columnspan=2, sticky=N+E+S+W, )
        self.browseButton.grid(row=0, column=2, sticky=N+S+E+W)
        self.confirmButton.grid(row=1, column=0, columnspan=2, sticky=N+S+E+W)
        self.imageLabel.grid(row=0, column=3, sticky=N+S+E+W)


    def _openFiles(self):
        '''This function will be used by the browse button to allow the user
        to search their files to open the IR Spectrum Analysis'''
        path = filedialog.askopenfilename()
        self.imagePath.set(path)
        #if


    def _confirm(self):
        '''This function will be used by the confirm button and will open
        up the next page to show the spectrum analysis'''





def main():
    root = Tk()
    main = IRSpectrumMain(root)
    main.mainloop()

main()