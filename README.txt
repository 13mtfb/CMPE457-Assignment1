Name: Matthew Burton
Student #: 10107168
NetID: 13mtfb


1. Code was run on Ubuntu 16.04 LTS using python 2.7.12, numpy 1.13.1, Pillow 4.2.1, PyOpenGL 3.0.2

2. The brightness factor was scaled by the windowWidth (similarly to the contrast factor being scaled by the windowHeight). However this resulted in values too low to be observed in the transformation. Therefore the brightness factor was multipled by 20 to see a visible change. 
      y = int(factorContrast * y) + (factorBrightness*20)

3. the variable baseImage is used to hold the current image upon which the image is applied. This is handled in the display() function, where if the mouse button is being held down the baseImage variable is not assigned to the img variable (which is set by the functon call img=buildImage() ).

Python throws an error if the saved image name does not contain a known file extension

5. The loadFilter() function assumes the legality of the file structure. i.e. the xdim and ydim variables match the number of filter coeffiecients, dimensions correct, etc. The scaleFactor and filter coefficients are printed to the terminal.

6. Python will throw an error if a filter has not been previously loaded since last time the program was run. Additionally, some of the more complicated filters take a couple of seconds to appear on the screen. The string "filter done" is printed to the terminal when the filter is applied. The box11 filter takes almost 20 seconds to load.

7. The "+" or "-" key action is assumed to apply after the right mouse button has been released. It uses the last clicked origin to increment/decrement the radius value and reapply (i.e. convolve) the filter using the new radius. This means that the "-" button does not "unconvolve" the image as the radius convolve is applied immediately to the image.
