from PIL import Image
import math
import os
import io
import shutil
tileSize = 256

# Resize image into different zoom levels for using in tileZoomLevel
def resize(fileName, zoom):
    # Check to see if a temp file exists, if not create one
    if not os.path.exists("/path/to/tmp"):
        os.makedirs("/path/to/tmp")
    # the approved zoom level
    approvedZoomList = range(zoom)
    # the full path to the directory where the image is kept
    sourceImageName = "/path/to/source/image/" +fileName

    print ("Generating overview images for %s" % (sourceImageName))

    # Combines the source image name with the .png extention
    img = Image.open(sourceImageName + ".png");
    # The original size of the image
    sourceImageWidth, sourceImageHeight = img.size
    # Uses the image dementions to determine the max zoom that can be achieved
    maxZoom = int(math.ceil(math.log(max(sourceImageWidth, sourceImageHeight) / tileSize, 2)))

    # To be used in a calculation further in code to help get an accurate image size of resized images
    baseOfImage = sourceImageWidth**(1/(8+maxZoom)) +.0000099995
    print ("Max zoom: %d" % (maxZoom))
    # For loop generates images
    for x in range(0, maxZoom + 1):

        if approvedZoomList and x not in approvedZoomList:
            print ("Ignoring level: %d" % (x))
            continue

        print ("Resizing level: %d" % (x))
        # Uses earlier calculation to find the correct size of new images
        zoomLevelResizeWidth = int(math.pow(baseOfImage, 8 + x))

        print ("zoomLevelResizeWidth: %d" % (zoomLevelResizeWidth))
        # Creates the new image in a squared format
        resizedImage = img.resize((zoomLevelResizeWidth, zoomLevelResizeWidth), Image.ANTIALIAS)

        # New image name and the path for it
        resizedFileName = "%d.png" % (x)
        resizedFilePath = "/path/to/tmp/%s" % (resizedFileName)

        # Saves the new image
        resizedImage.save(resizedFilePath)

# Generates the tiles which are used by leaflet to render the image in a broswer
def tileZoomLevel(fileName, event):

    # Path name and zoom assignment
    sourceImageName = "/path/to/source/image/" + fileName
    zoom = event
    for zoomLevel in range(zoom):

        # Check to see if image does exist, if so, create the tiles
        imgName = "/path/to/tmp/" + str(zoomLevel) + ".png"
        if os.path.exists(imgName):
            # Grab image and collect data of the image
            img = Image.open(imgName);
            sourceImageWidth, sourceImageHeight = img.size

            # Set the coordinates of the image. It will start in the upper left corner
            currentCoordsX = 0
            currentXCount = 0

            currentCoordsY = 0
            currentYCount = 0

            # Step through the x-axis
            while (currentCoordsX < sourceImageWidth):
                # Step through the y-axis
                while (currentCoordsY < sourceImageHeight):
                    # Create path for new set of tiles
                    pathName = sourceImageName + "/tiles/%d/%d/" % (zoomLevel, currentXCount)
                    # Create name for new image
                    path = sourceImageName + "/tiles/%d/%d/%d.png" % (zoomLevel, currentXCount, currentYCount)
                    # Check to see if the path exists, if not, create
                    if not os.path.exists(pathName):
                        os.makedirs(pathName)
                    tileExists = False
                    if (tileExists):
                        print ("Ignoring %s" % (path))
                    else:
                        # Set coordinates of the tile ranging from current to an additional 256(the tileSize)
                        left = currentCoordsX
                        right = currentCoordsX + tileSize
                        top = currentCoordsY
                        bottom = currentCoordsY + tileSize

                        # A check to see if the tile will extend past the size of the image. If so, the coordinates will equal the image's respective height/width
                        if right > sourceImageWidth:
                            right = sourceImageWidth
                        if bottom > sourceImageHeight:
                            bottom = sourceImageHeight

                        # FORMAT: img.crop(w, h, w+x, h+y)
                        tile = img.crop((left, top, right, bottom))

                        # Saves image
                        imgByteArr = io.BytesIO()
                        tile.save(imgByteArr, format='PNG')
                        imgByteArr = imgByteArr.getvalue()
                        tile.save(path)

                        del tile

                    # moves on to next in line vertically
                    currentCoordsY += tileSize
                    currentYCount += 1

                # Moves to next in line horizontally
                currentCoordsY = 0
                currentYCount = 0

                currentCoordsX += tileSize
                currentXCount += 1

                print ("/%d/%d" % (zoomLevel, currentXCount))



resize("NameofSourceImage", 7)
# Collect the number of files in the temp directory
files = os.listdir('/path/to/tmp')
tileZoomLevel("NameofSourceImage", len(files))

# Cleans up the temp file for you
if os.path.exists("/path/to/tmp/"):
    shutil.rmtree("/path/to/tmp/", ignore_errors=True)

print ("All tiles generated!")
