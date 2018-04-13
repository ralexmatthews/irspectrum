"""

"""
#---------------------------------Imports--------------------------------------
import PyPDF2
import sys
import warnings
import os
from os import path
warnings.filterwarnings("ignore")
#------------------------------------------------------------------------------

#---------------------------------Variables------------------------------------
#global variables go here
number = 0
#------------------------------------------------------------------------------

#---------------------------------Classes/Functions----------------------------
def PullImages(filename):

    '''
    Pull graph images from PDF's
    '''
    def recurse(page, xObject):
        global number

        xObject = xObject['/Resources']['/XObject'].getObject()

        images=[]

        for obj in xObject:

            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                data = xObject[obj]._data
                if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                    mode = "RGB"
                else:
                    mode = "P"

                #imagename = "%s"%(abspath[:-4], p, obj[1:])

                if xObject[obj]['/Filter'] == '/FlateDecode':
                    img = Image.frombytes(mode, size, data)
                    img.save(filename + ".png")
                    number += 1
                    images+=[filename + ".png"]
                elif xObject[obj]['/Filter'] == '/DCTDecode':
                    img = open(filename + ".jpg", "wb")
                    img.write(data)
                    img.close()
                    number += 1
                    images+=[filename + ".jpg"]
                elif xObject[obj]['/Filter'] == '/JPXDecode':
                    img = open(filename + ".jp2", "wb")
                    img.write(data)
                    img.close()
                    number += 1
                    images+=[filename + ".jp2"]
            else:
                recurse(page, xObject[obj])
        return images

    try:
        abspath = path.abspath(filename)
    except BaseException:
        print('Usage :\nPDF_extract_images file.pdf page1 page2 page3 …')
        sys.exit()

    f = PyPDF2.PdfFileReader(open(filename, "rb"))

    page0 = f.getPage(0)
    p = 1

    images=recurse(p, page0)

    return images
#------------------------------------------------------------------------------
