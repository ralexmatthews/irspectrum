from PIL import Image


def digitize(image):
    '''This function takes the path of an image and returns a list
    of the graph information. It goes pixel by pixel starting at
    [516, 1773] and ending at [2397, 1773] and gives the height of
    the graph at that point on a scale of 0-1'''

    # array to store values of graph height
    digitized = []

    # set up opening image
    im = Image.open(image)
    pix = im.load()

    # go across the line at y = 1773 and get the height
    for x in range(516, 2397):
        y = 1773
        while True:
            if not pix[x, y][0] > 200:
                digitized.append((1773 - y)/1517)
                break
            y -= 1
        
    return digitized
