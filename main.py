# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow
# by Matt Burton
# 13mtfb
# 10107168
import sys, os, numpy, math

try: # Pillow
  from PIL import Image
except:
  print 'Error: Pillow has not been installed.'
  sys.exit(0)

try: # PyOpenGL
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print 'Error: PyOpenGL has not been installed.'
  sys.exit(0)



# Globals

windowWidth  = 600 # window dimensions
windowHeight =  800

#start variable used to control src image being loaded from file
start = 1

#flip variable used to control flipping the image to save to file
flip = 0

# The intensity of the pixels is controlled by the Y component in
# YCbCr. Therefore the linear transform x' = m x + b can be used where
# m varies the contrast and b varies the brightness
factorBrightness = 0 # factor by which luminance is scaled (brightness)
factorContrast = 1 # factor by which the luminance is scaled (contrast)

# Mouse state on initial click

button = None
initX = 0
initY = 0
initFactorBrightness = 0
initfactorContrast = 1

#radius is set to -1 as the convolveFilter function also implements the radial filter and therefore filters the entire image if set to this value
radius = -1

# Image directory and path to image file

imgDir      = 'images'
imgFilename = 'mandrill.png'

imgPath = os.path.join( imgDir, imgFilename )

# Filter director and path to filter name

filDir = 'filters'
filFilename = 'box3' #placeholdername for filter

# File dialog

import Tkinter, tkFileDialog

root = Tkinter.Tk()
root.withdraw()


# Read and modify an image.

def buildImage():

  global start
  # allow to reset factors upon image load
  global factorContrast
  global factorBrightness
  # allow to flip image upon save
  global flip
  
  # if initializing program or realoading image from file, set src to file image
  # otherwise, set to the current image
  # reset factors upon load, so new image isn't distorted 
  if start == 1:
   src = Image.open( imgPath ).convert( 'YCbCr' )
   factorContrast = 1
   factorBrightness = 0
   print imgPath
  else :
   src = baseImage.convert( 'YCbCr' )

  srcPixels = src.load()

  width  = src.size[0]
  height = src.size[1]

  # Set up a new, blank image of the same size

  dst = Image.new( 'YCbCr', (width,height) )
  dstPixels = dst.load()

  # Build destination image from source image

  for i in range(width):
    for j in range(height):

      # read source pixel
      
      y,cb,cr = srcPixels[i,j]

      # ---- MODIFY PIXEL ----
      # Contrast factor changes the slope of the transform while the brightness factor scales the pixel
      # Scaled factorBrightness by 20 to increase effect of horizontal mouse scroll
      y = int(factorContrast * y) + (factorBrightness*20)

      # write destination pixel (while flipping the image in the vertical direction)
      #only flip pixels when loading new image, otherwise image will have flipped pixels previously
      if start == 1 or flip == 1:
       dstPixels[i,height-j-1] = (y,cb,cr)
      else :
       dstPixels[i,j] = (y,cb,cr)     

  # start variable controls whether image loaded from file (needs flipping) or set to current image (doesn't need flipping)
 # flip variable used to flip image so that saved image is correct orientation
  if start == 1:
    start = 0
  if flip == 1:
    flip = 0
  
  
  return dst.convert( 'RGB' )



# Set up the display and draw the current image

def display():
  
  #print button

  # Clear window

  glClearColor ( 1, 1, 1, 0 )
  glClear( GL_COLOR_BUFFER_BIT )

  #define globabl temp and current images
  global baseImage

  # rebuild the image

  #if button is not pressed (==None), then set current image to transformation
  #if right mouse button is held down, call filterConvolve() function instead of buildImage()
  #if button is pressed, bypass baseImage set (i.e. don't set current image until button is released)
  if button == None :
   baseImage = buildImage()
   img = baseImage
   #print "save current image"
  elif button == GLUT_RIGHT_BUTTON:
   baseImage = filterConvolve()
   img = baseImage
  else :
   img = buildImage()

  width  = img.size[0]
  height = img.size[1]

  # Find where to position lower-left corner of image

  baseX = (windowWidth-width)/2
  baseY = (windowHeight-height)/2

  glWindowPos2i( baseX, baseY )

  # Get pixels and draw

  imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

  glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

  glutSwapBuffers()

# histogram equalization function setup very similarly to buildimage function
def histogramEqualization():

  # Read current image and convert to YCbCr

  src = baseImage.convert( 'YCbCr' )
  srcPixels = src.load()

  width  = src.size[0]
  height = src.size[1]

  # Set up a new, blank image of the same size
  dst = Image.new( 'YCbCr', (width,height) )
  dstPixels = dst.load()

  # Compute N = total pixels
  N = width * height
  numIntensities = 256
  # setup zeroed arrays to hold original intensity and mapped intensities
  intensityFrequencyOriginal=[0 for i in range(0,256)]
  intensityFrequencyNew=[0 for i in range(0,256)]

  # intensity frequencies from image where index is frequency value
  for i in range(width):
   for j in range(height):
     y,cb,cr=srcPixels[i,j]
     intensityFrequencyOriginal[y]=intensityFrequencyOriginal[y]+1;
   #done
  #done
  
  sumIntensities = 0  
  print "Histogram Intensities:"
  # calculate intensity mappings using rolling sum of intensity frequencies
  for i in range(numIntensities):
   sumIntensities = sumIntensities + intensityFrequencyOriginal[i]
   intensityFrequencyNew[i]=round(((numIntensities*sumIntensities)/N)-1)
   if intensityFrequencyNew[i] < 0:
    intensityFrequencyNew[i] = 0
   print intensityFrequencyNew[i],

  print ""

  for i in range(width):
    for j in range(height):

      # read source pixel
      
      y,cb,cr = srcPixels[i,j]

      # ---- MODIFY PIXEL ----
      y = intensityFrequencyNew[int(y)]
      # write destination pixel
      dstPixels[i,j] = (y,cb,cr)

  # Done

  return dst.convert( 'RGB' )

# filter convolution function setup very similarly to buildimage function
def filterConvolve():
  global xdim, ydim, scaleFactor, data
  # Read current image and convert to YCbCr
  src = baseImage.convert( 'YCbCr' )
  dst = baseImage.convert( 'YCbCr' )
  srcPixels = src.load()
  dstPixels = dst.load()
  width  = src.size[0]
  height = src.size[1]
  #if radius -1, iterate over entire image, otherwise calculate custom boundaries based on initX, initY and radius
  if radius == -1:
   i_start = 0
   i_end = width
   j_start = 0
   j_end = height
  else :
   #custom indices were difficult to calculate as the initX and initY return a coordinate that is in relation to the window, not the image\
   #additionally, the height indices were flipped in order to account for the flipped vertical pixel direction.
   i_start = int((initX-radius)-(windowWidth-width)/2)
   i_end = int((initX+radius)-(windowWidth-width)/2)
   j_start = int(height-((initY+radius)-(windowHeight-height)/2))
   j_end = int(height-((initY-radius)-(windowHeight-height)/2))
   if (i_start < 0):
    i_start = 0
   if (i_end > width):
    i_end = width
   if (j_start < 0):
    j_start = 0
   if (j_end > height):
    j_end = height


  # iterate through all pixels in the output image. If there is a radius calculated, set custom boundaries for iteration
  for i in range(i_start, i_end):
    for j in range(j_start, j_end):
      #define
      convolve = 0
      #iterate through all pixels of the kernel filter for each output pixel
      for k in range(xdim):
        #print xdim
        for l in range(ydim):
          #establish pixel coordinates offset from origin of kernel (which is assumed to be the middle indices) so that input pixels aligns with origin of kernel
          index1=i+int(ydim/2)-l
          index2=j+int(xdim/2)-k
          #read src pixel if inside array range (i.e. valid image pixel), otherwise set to 0
          if (index1<0 or index1>=width or index2<0 or index2>=height):
            y=0
          else :
            y,cb,cr=srcPixels[index1,index2]
          #create sum of partial products for each coordinate in the kernel image
          convolve=convolve+y*data[ydim-l-1][xdim-k-1]

      # write destination pixel. If radius is set, ensure pixel is within the radius. This creates the rounding rather than the square that the loop would otherwise result in
      if ( math.sqrt( (i-(i_start+i_end)/2)**2 + (j-(j_start+j_end)/2)**2 ) <=radius) or radius == -1:
       dstPixels[i,j] = (convolve*scaleFactor,cb,cr)
  # Done
  print "filter done"

  return dst.convert( 'RGB' ) 

# function loads a filter from a file. Assumes the legality of the file structure as defined in A1.txt. No error checking is done
def loadFilter():
 global xdim,ydim,scaleFactor,data
 path = tkFileDialog.askopenfilename (initialdir = filDir )
 if path:
   #define data array
   data=[] 
   #open file, if the path exists
   with open( path ) as f:
   #read line-by-line and enumerate to determine line numbers
     for line_num, line in enumerate(f):
       #split line upon whitespace
       numbers_str = line.split()
       #first line contains xdim & ydim
       if line_num == 0:
        xdim = int(numbers_str[0])
        ydim = int(numbers_str[1])
        #print str(xdim) + " " + str(ydim)
       #second line contains scaleFactor
       elif line_num == 1:
        scaleFactor = float(numbers_str[0])
        print "scale factor: " + str(scaleFactor)
       else :
        x = [int(x) for x in numbers_str]
        data.append(x)
   print "filter:"     
   print data

   
  
# Handle keyboard input

def keyboard( key, x, y ):
  # allow baseImage to be modified
  global baseImage, radius
  
  if key == '\033': # ESC = exit
    sys.exit(0)

  elif key == 'l':
    path = tkFileDialog.askopenfilename( initialdir = imgDir )
    if path:
      loadImage( path )

  elif key == 's':
    outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
    if outputPath:
      saveImage( outputPath )

  # add histogram equalization key
  elif key == 'h':
    # set value of baseImage to the transformed image
    baseImage = histogramEqualization()

  elif key == 'f':
    # load filter to be modified
    loadFilter()

  elif key == 'a':
    # set value of baseImage to the transformed image
    baseImage = filterConvolve()

  elif key == '+' or key == '=':
    radius = radius + 1
    baseImage = filterConvolve()

  elif key == '-' or key == '_':
    radius = radius - 1
    if radius < 0:
     radius = 0
    baseImage = filterConvolve()

  else:
    print 'key =', key    # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

  glutPostRedisplay()
  

# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.

def loadImage( path ):

  global imgPath
  imgPath = path
  global start
  start = 1

def saveImage( path ):

  global flip
  flip = 1
  buildImage().save( path )
  
  

# Handle window reshape

def reshape( newWidth, newHeight ):

  global windowWidth, windowHeight

  windowWidth  = newWidth
  windowHeight = newHeight

  glutPostRedisplay()


# Handle mouse click/unclick

def mouse( btn, state, x, y ):

  global button, initX, initY, initFactorBrightness, initFactorContrast, factorBrightness, factorContrast, radius

  if state == GLUT_DOWN:

    button = btn
    initX = x
    initY = y

    if button == GLUT_LEFT_BUTTON:

      initFactorBrightness = factorBrightness
      initFactorContrast = factorContrast

    elif button == GLUT_RIGHT_BUTTON:

      initFactorBrightness = 0
      initFactorContrast = 1
      factorBrightness = 0
      factorContrast = 1
      radius = 1

  elif state == GLUT_UP:

    button = None

  # added redisplay so button release is redrawn using baseImage when mousebutton released
  glutPostRedisplay()

# Handle mouse motion

def motion( x, y ):

  diffX = x - initX
  diffY = y - initY

  global factorBrightness, factorContrast, radius

#duplicate existing factor calculation and add calculation for contrast using the vertical mouse motion
#Only calculate new brightness and contrast if left mouse button used

  if button == GLUT_LEFT_BUTTON: 
    factorBrightness = initFactorBrightness + diffX / float(windowWidth)
    factorContrast = initFactorContrast + diffY / float(windowHeight)
    radius = -1

  elif button == GLUT_RIGHT_BUTTON:
    #calculate new radius on mouse motion when right mouse button held down.
    radius = math.sqrt(diffX**2+diffY**2)

  if factorContrast < 0:
    factorContrast = 0

  glutPostRedisplay()
  

    
# Run OpenGL

glutInit()
glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
glutInitWindowSize( windowWidth, windowHeight )
glutInitWindowPosition( 50, 50 )

glutCreateWindow( 'imaging' )

glutDisplayFunc( display )
glutKeyboardFunc( keyboard )
glutReshapeFunc( reshape )
glutMouseFunc( mouse )
glutMotionFunc( motion )

glutMainLoop()
