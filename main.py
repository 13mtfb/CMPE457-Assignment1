# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow

import sys, os, numpy

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
##
# The intensity of the pixels is controlled by the Y component in
# YCbCr. Therefore the linear transform x' = m x + b can be used where
# m varies the contrast and b varies the brightness
factorBrightness = 0 # factor by which luminance is scaled (brightness)
factorContrast = 1 # factor by which the luminance is scaled (contrast)


# Image directory and pathe to image file

imgDir      = 'images'
imgFilename = 'mandrill.png'

imgPath = os.path.join( imgDir, imgFilename )



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
   src = currentImage.convert( 'YCbCr' )
   #print "next two numbers are transformations:"
   #print factorContrast
   #print factorBrightness


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
  global currentImage

  # rebuild the image

  #if button is not pressed (==None), then set current image to transformation
  #if button is pressed, bypass currentImage set (i.e. don't set current image until button is released)
  if button == None :
   currentImage = buildImage()
   img = currentImage
   #print "save current image"
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

  src = currentImage.convert( 'YCbCr' )
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

  # calculate intensity mappings using rolling sum of intensity frequencies
  for i in range(numIntensities):
   sumIntensities = sumIntensities + intensityFrequencyOriginal[i]
   intensityFrequencyNew[i]=round(((numIntensities*sumIntensities)/N)-1)
   if intensityFrequencyNew[i] < 0:
    intensityFrequencyNew[i] = 0
  
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





  
# Handle keyboard input

def keyboard( key, x, y ):

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
    # allow currentImage to be modified
    global currentImage
    # set value of currentImage to the transformed image
    currentImage = histogramEqualization()

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



# Mouse state on initial click

button = None
initX = 0
initY = 0
initFactorBrightness = 0
initfactorContrast = 0


# Handle mouse click/unclick

def mouse( btn, state, x, y ):

  global button, initX, initY, initFactorBrightness, initFactorContrast

  if state == GLUT_DOWN:

    button = btn
    initX = x
    initY = y
    initFactorBrightness = factorBrightness
    initFactorContrast = factorContrast

  elif state == GLUT_UP:

    button = None

  # added redisplay so button release is redrawn using currentImage
  glutPostRedisplay()

# Handle mouse motion

def motion( x, y ):

  diffX = x - initX
  diffY = y - initY

  global factorBrightness
  global factorContrast

#duplicate existing factor calculation and add calculation for contrast using the vertical mouse motion
 
  factorBrightness = initFactorBrightness + diffX / float(windowWidth)
  factorContrast = initFactorContrast + diffY / float(windowWidth)

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
