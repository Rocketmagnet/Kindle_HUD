# 
# Basic graphics functions for the Kindle HUD
# 

import png
import urllib
import math
import os
import datetime
import time


screenWidth  = 800
screenHeight = 600
ScreenNumPixels = screenWidth * screenHeight
screenArray = bytearray(b'\xFF' * ScreenNumPixels)
        
# The Font class handles rendering of bitmapped fonts to the screen image.
# Because the Kindle is to be used in Landscape mode, the screen is sideways,
# so the Font class is designed to render fonts sideways.
# 
# The Font class handles kerning.
# 
# Font files are raw 8-bit greyscale bitmaps, with each character laid out 
# in a single long row, with at least 1 column of white (255) separating each
# character. 
# The first columns must be completely black, the second column completely white.
# This defines the height of the font. Every character from ! to ~
# 
# The whole image must be mirrored then rotated 90 deg anticlockwise.
# 
# Example:
#     trebuchet_28px = Font('Trebuchet_28px.raw')
#     trebuchet_28px.Print("Hello world", 10, 10)
#         
class Font:
    
    def ColumnIsBlank(self, column):
        for i in range(column*self.fontHeight, (column+1)*self.fontHeight):
            if (self.fontArray[i] != 255):
                return 0
        return 1
               
    def ReadKerningLeft(self, startColumn, maxKern):
        kerningLeft = []
        #print(startColumn)
        for y in range(0,self.fontHeight):
            #print("y", y)
            pixelAddress = startColumn*self.fontHeight + y
            whiteSpace = 0
            while (self.fontArray[pixelAddress] > 196) & (self.fontArray[pixelAddress] != 254) & (whiteSpace<maxKern):
                #print(whiteSpace,pixelAddress)
                whiteSpace += 1
                pixelAddress += self.fontHeight
                
            kerningLeft.append(whiteSpace)
        #print("kerning L", kerningLeft)
        return kerningLeft

    def ReadKerningRight(self, startColumn, maxKern):
        kerningRight = []
        for y in range(0,self.fontHeight):
            #print("y", y)
            pixelAddress = startColumn*self.fontHeight + y
            whiteSpace = 0
            while (self.fontArray[pixelAddress] > 196) & (self.fontArray[pixelAddress] != 254) & (whiteSpace<maxKern):
                #print(whiteSpace,pixelAddress)
                whiteSpace += 1
                pixelAddress -= self.fontHeight
                
            kerningRight.append(whiteSpace)
        #print("kerning R", kerningRight)
        return kerningRight
        
    def __init__(self, fontFileName):                           # Font must contain black pixels in column 0, white pixels in column 1, and be rotated 90deg clockwise

        self.fontArray = bytearray(1)
        self.fontHeight = 0
        self.numColumns = 0
        self.characters = []
    
        self.fontFile  = open(fontFileName, 'rb')               # Load up the font file, and work out how tall the font is based on the black line at column 0
        self.fontArray = bytearray(self.fontFile.read())
        for i in range(0, 300):
            if self.fontArray[i] == 0:
                self.fontHeight += 1
            else:
                break
        
        self.interCharacterPixels = int(self.fontHeight / 8)
        self.spacePixels          = int(self.fontHeight / 3)
        
        numColumns = int(len(self.fontArray) / self.fontHeight)
        print fontFileName
        print(self.fontHeight)
        print(numColumns)

        column = 1
        charactersLeft = True
        #for i in range (0,10):
        while True:
            #character = [0, 
            characterWidth = 0
            
            while self.ColumnIsBlank(column):
                column += 1
                if column >= numColumns:
                    break

            if column >= numColumns:
                break
            
            startColumn = column
            c1          = column*self.fontHeight
            
            while self.ColumnIsBlank(column) == False:
                column += 1
                characterWidth += 1
                
            endColumn = column
            c2        = column*self.fontHeight
            
            kerningLeft  = self.ReadKerningLeft( startColumn,   endColumn-startColumn)
            kerningRight = self.ReadKerningRight(  endColumn-1, endColumn-startColumn)
            
            characterPixels = self.fontArray[c1:c2]
            character = [self.fontHeight, characterWidth, characterPixels, kerningLeft, kerningRight]      # height, width, pixelData, leftKern, rightKern
            
            self.characters.append(character)
            
            #print(characterWidth,"wide")
            #print(len(character),"pixels")
            #print("[",c1,":",c2,"]")
        #print(len(self.characters), "characters read")
        #self.ReadKerningRight(233,6)

        
    def BlitCharacter(self, character, x,y):
        characterHeight      = character[0]
        characterWidth       = character[1]

        if (x+characterWidth) > 800:
            return
            
        startScreenPixelAddress    = (screenWidth-x-1)*screenHeight + y
        endScreenPixelAddress      = startScreenPixelAddress + characterHeight
        startCharacterPixelAddress = 0
        endCharacterPixelAddress   = characterHeight
        
        for i in range(0, characterWidth):
            k = startCharacterPixelAddress
            for j in range(startScreenPixelAddress,endScreenPixelAddress):
                if character[2][k] < 255:
                    screenArray[j] = character[2][k]
                k += 1
                
            #screenArray[startScreenPixelAddress:endScreenPixelAddress] -= character[2][startCharacterPixelAddress:endCharacterPixelAddress]
            startCharacterPixelAddress += characterHeight
            endCharacterPixelAddress   += characterHeight
            startScreenPixelAddress    -= screenHeight
            endScreenPixelAddress      -= screenHeight

    def CalcKerning(self, prev, this):
        if prev == '':
            return 0
            
        prevChar = self.characters[ord(prev)-ord('!')]
        thisChar = self.characters[ord(this)-ord('!')]
        kerningRight = prevChar[4]
        kerningLeft  = thisChar[3]
    
        minSpan = 99
        for i in range(0, len(kerningLeft)):
            span = kerningLeft[i] + kerningRight[i]
            if span < minSpan:
                minSpan = span

        jump = self.interCharacterPixels + prevChar[1] - minSpan
        return jump
    
    
    def Print(self, textString, x, y):    
        if y+self.fontHeight >= 600:
            return
            
        prev      = ''
        prevWidth = 0
        for c in textString:
            charNum = ord(c)-ord('!')
            character = self.characters[charNum]
            if c != ' ':
                if (charNum>=0) & (charNum<len(self.characters)):
                    x += self.CalcKerning(prev, c)
                    self.BlitCharacter(character,x,y)
                    prev = c
                    prevWidth = character[1]
            else:
                prev = ''
                x += prevWidth + self.spacePixels

    def CalcWidth(self, textString):    
        prev      = '' 
        prevWidth = 0  
        x         = 0  
        for c in textString:
            charNum = ord(c)-ord('!')
            character = self.characters[charNum]
            if c != ' ':
                if (charNum>=0) & (charNum<len(self.characters)):
                    x += self.CalcKerning(prev, c)
                    #self.BlitCharacter(character,x,y)
                    prev = c
                    prevWidth = character[1]
            else:
                prev = ''
                x += prevWidth + self.spacePixels
        return x+character[1]

    def PrintCentred(self, textString, x, y):    
        width = self.CalcWidth(textString)
        self.Print(textString, x - int(width/2), y)

    def PrintRightJus(self, textString, x, y):    
        width = self.CalcWidth(textString)
        self.Print(textString, x - width, y)

    def PrintBlock(self, textString, x, y, width):
        words = textString.split()
        xPos = x
        yPos = y
        maxX = x+width
        justCR = False
        
        for word in words:
            wordWidth = self.CalcWidth(word)
            if (xPos+wordWidth) > maxX:
                xPos = x
                yPos += self.fontHeight
            self.Print(word, xPos, yPos)
            xPos += wordWidth+self.spacePixels
            
        return yPos+self.fontHeight


# Icons class is similar to the Font class, but only renders single icons, not
# strings of characters.
# 
class Icons:
    def __init__(self, iconsFileName):                           # Image  must contain black pixels in column 0, white pixels in column 1, and be rotated 90 deg clockwise
        print iconsFileName
        self.iconArray  = bytearray(1)
        self.iconHeight = 0
        self.numColumns = 0
        self.icons      = []
    
        self.iconFile  = open(iconsFileName, 'rb')               # Load up the font file, and work out how tall the font is based on the black line at column 0
        self.iconArray = bytearray(self.iconFile.read())
        
        for i in range(0, 300):                                 # Measure height of initial black line (max 300 pixels)
            if self.iconArray[i] == 0:
                self.iconHeight += 1
            else:
                break

        
        self.numIcons = int(((len(self.iconArray)-1) / self.iconHeight) / self.iconHeight)
        #print(len(self.iconArray))
        print(self.iconHeight)
        print self.numIcons, "icons"
        
    def Draw(self, iconNumber, x, y):
        if (iconNumber<0) | (iconNumber>=self.numIcons):
            return
            
        startIconAddress        = ((iconNumber*self.iconHeight) + 1) *self.iconHeight
        endIconAddress          = startIconAddress + self.iconHeight
        startScreenPixelAddress = (screenWidth-x-1)*screenHeight + y
        endScreenPixelAddress   = startScreenPixelAddress + self.iconHeight
        
        for i in range(0, self.iconHeight):
            #print(i, startScreenPixelAddress, endScreenPixelAddress, startIconAddress, endIconAddress)
            screenArray[startScreenPixelAddress:endScreenPixelAddress] = self.iconArray[startIconAddress:endIconAddress]
            #screenArray[startScreenPixelAddress] = 0
            #screenArray[endScreenPixelAddress]   = 0
            startScreenPixelAddress -= screenHeight
            endScreenPixelAddress   -= screenHeight
            startIconAddress        += self.iconHeight
            endIconAddress          += self.iconHeight
            
    def DrawCentred(self, iconNumber, x, y):
        self.Draw(iconNumber, x - int(self.iconHeight/2), y)
        
        
# Save the screen image to disk as a raw 8-bit bitmap.
# This can then be written to the screen using the 'eips' command.
#         
def SaveImage():
    with open("test_screen.raw", 'wb') as output:
        output.write(screenArray)

        
def WriteImageToKindleScreen(filename):
    today = str(datetime.datetime.today())
    print today
    
    print "Filename: " + filename
    f = open(filename, 'wb')
    w = png.Writer(screenHeight, screenWidth, greyscale=True)
    w.write_array(f, screenArray)
    f.close()        
    os.system("eips -c -g " + filename)


# Load up all the fonts and icons    
trebuchet_37px      =  Font('Trebuchet_37px.raw')
trebuchet_28px      =  Font('Trebuchet_28px.raw')
trebuchet_17px      =  Font('Trebuchet_17px.raw')
trebuchet_17px_Bold =  Font('Trebuchet_17px_Bold.raw')
trebuchet_11px      =  Font('Trebuchet_11px.raw')
numbers_103px       =  Font('Large_Numbers.raw')
weatherooLarge      = Icons('Icons_Large.raw')
weatherooSmall      = Icons('Icons_Small.raw')
trafficIcons        = Icons('Traffic_Icons.raw')
extrasIcons         = Icons('Extras_Icons_01.raw')
batteryIcons        =  Font('Batteries.raw')


# Fetch the rain radar image from Wunderground
# and combine it with an image of the map of London.
# 
# Fixme: The fact that it uses a bitmap of the map of 
# London makes this a bit un-portable.  It would be
# nice to find some way to get it to auto-generate the
# map. But it's non-trivial because you really need a
# nice simple map, with only a few details on it. Where
# can you get that from?
# 
def ReadRainRadar():
    print "ReadRainRadar()"
    try:
        rain          = png.Reader(file=urllib.urlopen('http://api.wunderground.com/api/f912ab4e1aac3427/radar/image.png?minlat=51.189549&maxlat=51.835226&minlon=-0.820341&maxlon=0.615710&width=380&height=277&newmaps=0'))
        mapFile       = open('London_Map_380x277.png', 'rb')
        mapPNG        = png.Reader(mapFile)
        pngInfo       = rain.read()
        palette       = rain.palette()
        xSize         = pngInfo[0]
        ySize         = pngInfo[1]    
        iterator      = pngInfo[2]
        rainPixelData = list(iterator)
        mapPngInfo    = mapPNG.read()
        iterator2     = mapPngInfo[2]
        mapPixelData  = list(iterator2)

        print "rendering"
        
        for x in range(0, xSize):
            p = (xSize-x+10)*screenHeight + 313
            for y in range(0, ySize):
                rainPixel = palette[rainPixelData[y][x]]
                r = rainPixel[0]
                g = rainPixel[1]
                b = rainPixel[2]
                a = rainPixel[3]
                
                if a < 255:
                    g = 255
                else:
                    if g<0:
                        g=0
                    
                screenArray[p] = ((g) * mapPixelData[y][x]) / 256
                p += 1
    except:
        print "Rain radar Failed"


                
def trunc(x):               # Return the integer part of a number
	return int(x)
 
def frac(x):
	return x - int(x)

def invfrac(x):
	return 1 - (x-int(x))

def abs(x):
    if x < 0:
        return -x
    else:
        return x
    
def DrawPixel(x,y,col,alpha):
    pix = ((screenWidth-x)*screenHeight) + y
    
    p = screenArray[pix]
    
    p2 = int(p*(1.0-alpha) + col*alpha)
    screenArray[pix] = p2

spanLines = [None] * screenWidth

def InitSpanLines():
    global spanLines
    for i in range(0, len(spanLines)):
        spanLines[i] = [999,0]

        
InitSpanLines()     # Required by WuLine()

# Draw an anti-aliased line.
# 
# Assumes that the background is white.
# Doesn't support drawing correctly over a background image.
# 
def WuLine(x1, y1, x2, y2, col, opac):
    global spanLines

    #Width and Height of the line
    xd = (x2-x1)
    yd = (y2-y1)

   
    if abs(xd) > abs(yd):
    #horizontal(ish) lines


        if x1 > x2:				            # if line is back to front
            x2,x1 = x1, x2			        # then swap it round
            y2,y1 = y1, y2
            xd = (x2-x1)				    # and recalc xd & yd
            yd = (y2-y1)

        grad = yd/xd                             # gradient of the line
        

        #End Point 1
        #-----------

        xend = trunc(x1+.5)                      # find nearest integer X-coordinate
        yend = y1 + grad*(xend-x1)               # and corresponding Y value
        
        xgap = invfrac(x1+.5)                    # distance i
        
        ix1  = int(xend)                         # calc screen coordinates
        iy1  = int(yend)

        brightness1 = invfrac(yend) * xgap       # calc the intensity of the other 
        brightness2 =    frac(yend) * xgap       # end point pixel pair.
        
        a1 = brightness1*opac	                 # calc pixel values
        a2 = brightness2*opac	

        DrawPixel(ix1,iy1,   col, a1)			 # draw the pair of pixels
        DrawPixel(ix1,iy1+1, col, a2)

        if  spanLines[ix1][0] > iy1+1:
            spanLines[ix1][0] = iy1+1
        if  spanLines[ix1][1] < iy1+1:
            spanLines[ix1][1] = iy1+1
        
        yf = yend+grad                           # calc first Y-intersection for
                                                 # main loop

        #End Point 2
        #-----------

        xend = trunc(x2+.5)                      # find nearest integer X-coordinate
        yend = y2 + grad*(xend-x2)               # and corresponding Y value
        
        xgap = invfrac(x2-.5)                    # distance i
        
        ix2  = int(xend)                         # calc screen coordinates
        iy2  = int(yend)

        brightness1 = invfrac(yend) * xgap       # calc the intensity of the first 
        brightness2 =    frac(yend) * xgap       # end point pixel pair.
        
        a1 = brightness1*opac	         # calc pixel values
        a2 = brightness2*opac	

        DrawPixel(ix2,iy2,   col, a1)			         # draw the pair of pixels
        DrawPixel(ix2,iy2+1, col, a2)

        if  spanLines[ix2][0] > iy2+1:
            spanLines[ix2][0] = iy2+1
        if  spanLines[ix2][1] < iy2+1:
            spanLines[ix2][1] = iy2+1


        #MAIN LOOP
        #---------

        for x in range(ix1+1, ix2):			# main loop

            brightness1 = invfrac(yf)		    # calc pixel brightnesses
            brightness2 =    frac(yf)

            a1 = brightness1*opac	        # calc pixel values
            a2 = brightness2*opac	

            DrawPixel(x,int(yf),   col, a1)			# draw the pair of pixels
            DrawPixel(x,int(yf)+1, col, a2)

            if  spanLines[x][0] > int(yf)+1:
                spanLines[x][0] = int(yf)+1
            if  spanLines[x][1] < int(yf)+1:
                spanLines[x][1] = int(yf)+1
                
            yf = yf + grad				        # update the y-coordinate

    else:
        if y1 > y2:				            # if line is back to front
            x2,x1 = x1, x2			        # then swap it round
            y2,y1 = y1, y2
            xd = (x2-x1)				# and recalc xd & yd
            yd = (y2-y1)

        grad = xd/yd                             # gradient of the line
        

        #End Point 1
        #-----------

        yend = trunc(y1+.5)                      # find nearest integer X-coordinate
        xend = x1 + grad*(yend-y1)               # and corresponding Y value
        
        ygap = invfrac(y1+.5)                    # distance i
        
        iy1  = int(yend)                         # calc screen coordinates
        ix1  = int(xend)

        brightness1 = invfrac(xend) * ygap       # calc the intensity of the other 
        brightness2 =    frac(xend) * ygap       # end point pixel pair.
        
        a1 = brightness1*opac	             # calc pixel values
        a2 = brightness2*opac	

        DrawPixel(ix1,  iy1, col, a1)			         # draw the pair of pixels
        DrawPixel(ix1+1,iy1, col, a2)

        xf = xend+grad                           # calc first Y-intersection for
                                                 # main loop

        #End Point 2
        #-----------

        yend = trunc(y2+.5)                      # find nearest integer X-coordinate
        xend = x2 + grad*(yend-y2)               # and corresponding Y value
        
        ygap = invfrac(y2-.5)                    # distance i
        
        iy2  = int(yend)                         # calc screen coordinates
        ix2  = int(xend)

        brightness1 = invfrac(xend) * ygap       # calc the intensity of the first 
        brightness2 =    frac(xend) * ygap       # end point pixel pair.
        
        a1 = brightness1*opac	         # calc pixel values
        a2 = brightness2*opac	

        DrawPixel(ix2,  iy2, col, a1)			         # draw the pair of pixels
        DrawPixel(ix2+1,iy2, col, a2)



        #MAIN LOOP
        #---------

        for y in range(iy1+1, iy2):			# main loop

            brightness1 = invfrac(xf)		    # calc pixel brightnesses
            brightness2 =    frac(xf)

            a1 = brightness1*opac	        # calc pixel values
            a2 = brightness2*opac	

            DrawPixel(int(xf),   y, col, a1)			# draw the pair of pixels
            DrawPixel(int(xf+1), y, col, a2)

            if  spanLines[int(xf+1)][0] > y:
                spanLines[int(xf+1)][0] = y
            if  spanLines[int(xf+1)][1] < y:
                spanLines[int(xf+1)][1] = y
            
            xf = xf + grad				        # update the y-coordinate

            
# Draw a polygon with anti-aliased edges.
# 
# Fixme: One small bug means that very occasionally, a spanline that touches a vertex is drawn incorrectly
# 
def DrawPolygon(pointsList, outlined):
    InitSpanLines()
                         
    j = 1
    for i in range(0, len(pointsList)):
        #print "i,j=", i, j
        WuLine(pointsList[i][0]+.01, pointsList[i][1]-.01, pointsList[j][0]+.01, pointsList[j][1]-.01, 0, 0)
        j += 1
        if j == len(pointsList):
            j = 0
            
    xAddress = screenHeight * (screenWidth)
    for span in spanLines:
        if span[0] != 999:
            
            #screenArray[xAddress+int(span[0]):xAddress+int(span[1])] = 128
            for p in range(xAddress+int(span[0]), xAddress+int(span[1])):
                #print xAddress+int(span[0]), xAddress+int(span[1])+1
                screenArray[p] = 128
                
        xAddress -= screenHeight
    
    if outlined == True:
        j = 1
        for i in range(0, len(pointsList)):
            #print "i,j=", i, j
            WuLine(pointsList[i][0]+.01, pointsList[i][1]+.01, pointsList[j][0]+.01, pointsList[j][1]+.01, 0, 1)
            j += 1
            if j == len(pointsList):
                j = 0
         

         
# Draw a 16-petal wind compass.
# Rather than draw a single arrow for the wind, it draws a distribution
# of the wind speed and direction over the next few hours.
# 
# The wind distribution is represented as a kind of scatter plot(?) 
# where each petal is filled in to some extend to show the max and min
# wind speed for the time period.
# 
def DrawWindCompass(x,y, windInfo):
    absMaxWind = 0
        
    for i in range(0, 16):
        wind = windInfo[i]
        minWind = wind[0]
        maxWind = wind[1]
        absMaxWind = max(absMaxWind, maxWind)
        
        t  = i * (6.28318/16)
        t1 = t - (6.28318/40)
        t2 = t + (6.28318/40)

        p1x = x + math.cos(t1)*30
        p1y = y + math.sin(t1)*30
        p2x = x + math.cos(t1)*80
        p2y = y + math.sin(t1)*80
        p3x = x + math.cos(t2)*80
        p3y = y + math.sin(t2)*80
        p4x = x + math.cos(t2)*30
        p4y = y + math.sin(t2)*30
        
        WuLine(p1x,p1y, p2x,p2y, 128, 1)
        WuLine(p2x,p2y, p3x,p3y, 128, 1)
        WuLine(p3x,p3y, p4x,p4y, 128, 1)
        WuLine(p4x,p4y, p1x,p1y, 128, 1)
        
        
        if minWind < 999:
            minWind += 30
            maxWind += 31
                
            t1 = t - (6.28318/42)
            t2 = t + (6.28318/42)
            p1x = x + math.cos(t1)*minWind
            p1y = y + math.sin(t1)*minWind
            p2x = x + math.cos(t1)*maxWind
            p2y = y + math.sin(t1)*maxWind
            p3x = x + math.cos(t2)*maxWind
            p3y = y + math.sin(t2)*maxWind
            p4x = x + math.cos(t2)*minWind
            p4y = y + math.sin(t2)*minWind
            
            DrawPolygon([[p1x,p1y], [p2x,p2y], [p3x,p3y], [p4x,p4y]], True)
            
    trebuchet_37px.PrintCentred(str(absMaxWind),x,y -15)
    trebuchet_17px.PrintCentred('N',x-1,y -78)
    trebuchet_17px.PrintCentred('S',x-1,y +62)
    trebuchet_17px.PrintCentred('W',x -68,y-7)
    trebuchet_17px.PrintCentred('E',x +71,y-7)

    

    
def RenderBatteryLife(x, y, percentage):
    os.system("gasgauge-info -c > charge.txt")
    chargeFile = open("charge.txt", "r")
    charge = chargeFile.read()
    trebuchet_11px.Print(charge, 755,1)

