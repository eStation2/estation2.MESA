#!/usr/bin/env python

# Fronts.py - Provides methods for detecting fronts in oceanographic images.
#
# Copyright (C) 2007 Jason J. Roberts
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License (available in the file LICENSE.TXT)
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import range
from past.utils import old_div
import copy
import os
import os.path
import re
import time
import sys 
import numpy as Numeric

try:
    from osgeo import gdal
    from osgeo.gdalconst import *
    gdal.TermProgress = gdal.TermProgress_nocb
except ImportError:
    import gdal
    from gdalconst import *

try:
    from osgeo import gdal_array as gdalnumeric
except ImportError:
    import gdalnumeric

def DetectEdgesInSingleImage(image, histogramWindowStride, minTheta, histogramWindowSize, minPopProp, minPopMeanDifference, minSinglePopCohesion, minImageValue, wrapEdges=False, maxImageValue=None, masks=None, maskTests=None, maskValues=None, medianFilterWindowSize=3,  minPropNonMaskedCells=0.65, minGlobalPopCohesion=0.92, threads=1):

        # Perform additional validation.

	if histogramWindowStride is None:
	    histogramWindowStride=16

        if minTheta is None:
	        minTheta=0.76

        if histogramWindowSize is None:
	        histogramWindowSize=32

        if minPopProp is None:
	        minPopProp=0.25
        
        if minPopMeanDifference is None:
	        minPopMeanDifference=3.0
      
        if minSinglePopCohesion is None:
	        minSinglePopCohesion=0.90

        if masks is not None:
            if maskTests is None:
                print ('If you provide a list of masks, you must also provide a parallel list of mask tests.')
            if maskValues is None:
                print ('If you provide a list of masks, you must also provide a parallel list of mask values.')

        if medianFilterWindowSize is not None and medianFilterWindowSize % 2 == 0:
            print ('The median filter window size must be a positive odd integer greater than or equal to 3.')

        if histogramWindowStride > histogramWindowSize:
            print ('The histogram stride cannot be larger than the histogram window size.')

        # Import needed modules.
        
        import numpy
        import FrontsUtils

        # The edge detection algorithm uses moving windows. To
        # simplify implementation of that code, create a copy of the
        # caller's image with a buffer around each edge. Also allocate
        # a buffered mask in which True indicates that the
        # corresponding cell of the caller's image is invalid.

        if medianFilterWindowSize is None:
            bufferSize = old_div((histogramWindowSize + 1), 2)
        else:
            bufferSize = max([old_div((medianFilterWindowSize + 1), 2), old_div((histogramWindowSize + 1), 2)])
        rows = bufferSize + image.shape[0] + bufferSize
        cols = bufferSize + image.shape[1] + bufferSize

        bufferedImage = numpy.zeros((rows, cols), dtype=image.dtype)
        bufferedImage[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]] = image

        bufferedMask = numpy.array([True] * rows * cols).reshape((rows, cols))
        unbufferedMask = bufferedMask[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]       
	# unbufferedMask is a reference to cells of bufferedMask, not a deep copy
        unbufferedMask[:] = False

        # Apply the caller's masks.

        if minImageValue is not None:
            print (' Debug: minImageValue not defined.')
            unbufferedMask[:] = numpy.logical_or(unbufferedMask, image < minImageValue)

        if maxImageValue is not None:
            print (' Debug: maxImageValue not defined.')
            unbufferedMask[:] = numpy.logical_or(unbufferedMask, image > maxImageValue)

        if masks is not None:
            for i in range(len(masks)):
                if maskTests[i] == u'equal':
                    print((' Debug: Masking cells where mask %(mask)i is equal to ', i, '.'))
                    unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] == maskValues[i])
                    
                elif maskTests[i] == u'notequal':
                    print((' Debug: Masking cells where mask %(mask)i is not equal to ', i, '.'))
                    unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] != maskValues[i])
                    
                elif maskTests[i] == u'greaterthan':
                    print((' Debug: Masking cells where mask %(mask)i is greater than ', i, '.'))
                    unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] > maskValues[i])
                    
                elif maskTests[i] == u'lessthan':
                    print((' Debug: Masking cells where mask %(mask)i is less than ', i, '.'))
                    unbufferedMask[:] = numpy.logical_or(unbufferedMask, masks[i] < maskValues[i])
                    
                elif maskTests[i] == u'anybitstrue':
                    print((' Debug: Masking cells where mask ', i, '(mask) bitwise-ANDed with ', X, ' is not zero.'))
                    unbufferedMask[:] = numpy.logical_or(unbufferedMask, numpy.bitwise_and(masks[i], maskValues[i]) != 0)
                    
                else:
                    print((s, ' is not an allowed mask test.'))

        # If the caller specified that the edges should wrap, copy the
        # cells from the left edge of the image (and mask) to the
        # strip of buffer cells to the right of the image (and mask),
        # and visa versa. For example, if the image was 6x6 with a
        # buffer of 2 and these values:
        #
        #     [[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 0,  0,  0,  1,  2,  3,  4,  5,  0,  0],
        #      [ 0,  0,  6,  7,  8,  9, 10, 11,  0,  0],
        #      [ 0,  0, 12, 13, 14, 15, 16, 17,  0,  0],
        #      [ 0,  0, 18, 19, 20, 21, 22, 23,  0,  0],
        #      [ 0,  0, 24, 25, 26, 27, 28, 29,  0,  0],
        #      [ 0,  0, 30, 31, 32, 33, 34, 35,  0,  0],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]]
        #
        # The resulting image, after the copy operation, would be:
        #
        #     [[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 4,  5,  0,  1,  2,  3,  4,  5,  0,  1],
        #      [10, 11,  6,  7,  8,  9, 10, 11,  6,  7],
        #      [16, 17, 12, 13, 14, 15, 16, 17, 12, 13],
        #      [22, 23, 18, 19, 20, 21, 22, 23, 18, 19],
        #      [28, 29, 24, 25, 26, 27, 28, 29, 24, 25],
        #      [34, 35, 30, 31, 32, 33, 34, 35, 30, 31],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]]
        
        if wrapEdges is True:
            bufferedImage[bufferSize:bufferSize+image.shape[0], 0:bufferSize] = bufferedImage[bufferSize:bufferSize+image.shape[0], -(bufferSize*2):-bufferSize]
            bufferedImage[bufferSize:bufferSize+image.shape[0], -bufferSize:] = bufferedImage[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize*2]
            bufferedMask[bufferSize:bufferSize+image.shape[0], 0:bufferSize] = bufferedMask[bufferSize:bufferSize+image.shape[0], -(bufferSize*2):-bufferSize]
            bufferedMask[bufferSize:bufferSize+image.shape[0], -bufferSize:] = bufferedMask[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize*2]

        # Apply the median filters.

        if medianFilterWindowSize is not None:
            #print ' Debug: Applying ',ix,i,' median filter.'
            bufferedImage = FrontsUtils.MedianFilter(bufferedImage, bufferedMask, bufferSize, medianFilterWindowSize)

            # If the caller specified that the edges should wrap, copy
            # image values to the buffer strips again, because the image
            # values probably changed as a result of running the median
            # filter.

            bufferedImage[bufferSize:bufferSize+image.shape[0], 0:bufferSize] = bufferedImage[bufferSize:bufferSize+image.shape[0], -(bufferSize*2):-bufferSize]
            bufferedImage[bufferSize:bufferSize+image.shape[0], -bufferSize:] = bufferedImage[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize*2]

        # Run the Cayula-Cornillon (1992) single-image edge detection
        # algorithm. This function performs the histogram and cohesion
        # steps, but does not perform contour following, thinning or
        # other post-processing.
        #
        # The values of the CandidateCounts image show how many times
        # each cell was a candidate for containing a front, i.e. the
        # number of times it appeared in a histogram window that had a
        # sufficiently large number of non-masked cells to proceed to
        # the histogramming portion of the algorithm. Masked cells can
        # never be candidates for containing a front, by definition,
        # so they will always have a zero CandidateCount. Because
        # successive histogram windows overlap, it is expected that a
        # given non-masked cell will have a CandidateCount greater
        # than 1.
        #
        # The values of the FrontCounts image show how many times each
        # cell was found to contain a front. This value will range
        # from zero (it never contained a front) to the CandidateCount
        # for the cell (it always contained a front in every histogram
        # window that contained it).
        #
        # The values of the WindowStatusCodes and WindowStatusValues
        # images show the result of running the algorithm on the
        # window centered on the cell in question. See the
        # documentation for these parameters for more information.

        bufferedCandidateCounts = numpy.zeros((rows, cols), dtype='int16')
        bufferedFrontCounts = numpy.zeros((rows, cols), dtype='int16')
        bufferedWindowStatusCodes = numpy.zeros((rows, cols), dtype='int8')
        bufferedWindowStatusValues = numpy.zeros((rows, cols), dtype='float32')

        print (' Debug: Running histogramming and cohesion algorithm.')
        timeStarted = time.clock()

        # If we're only using one thread, invoke the C code directly.

        if threads <= 1 or threads > image.shape[0]:
            FrontsUtils.CayulaCornillonFronts(bufferedImage, bufferedMask, bufferedCandidateCounts, bufferedFrontCounts, bufferedWindowStatusCodes, bufferedWindowStatusValues, bufferSize, histogramWindowSize, histogramWindowStride, minPropNonMaskedCells, minPopProp, minPopMeanDifference, minTheta, minSinglePopCohesion, minGlobalPopCohesion)

        # If we're using multiple threads, divide the window into
        # equal-sized blocks invoke the C code on each block from a
        # separate thread.

        else:

            # First divide the bufferedImage and bufferedMask into
            # blocks, one block for each thread. Adjust the block
            # height to be a multiple of the histogram window stride;
            # otherwise some cells might be processed fewer times than
            # others. The last block will be slightly larger than the
            # preceding blocks unless the image height divided by the
            # number of threads is a multiple of the stride.
            #
            # The subarrays that are created here are references, not
            # deep copies.

            blockHeight = old_div(image.shape[0], threads)
            blockHeight = blockHeight - blockHeight % histogramWindowStride

            bufferedImageList = []
            bufferedMaskList = []
            
            for i in range(threads - 1):
                bufferedImageList.append(bufferedImage[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :])
                bufferedMaskList.append(bufferedMask[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :])

            bufferedImageList.append(bufferedImage[(i+1) * blockHeight : , :])
            bufferedMaskList.append(bufferedMask[(i+1) * blockHeight : , :])

            # When each thread passes the window over its block, the
            # window will include some cells from the above and below
            # blocks. As the algorithm executes, it writes values to
            # the numpy arrays we allocated. If we just passed in
            # references to subarrays of those arrays, there is the
            # possibility that two threads will try to write to the
            # same cell at the same time. To prevent this, allocate
            # separate arrays for each thread.

            bufferedCandidateCountsList = []
            bufferedFrontCountsList = []
            bufferedWindowStatusCodesList = []
            bufferedWindowStatusValuesList = []
                        
            for i in range(threads):
                bufferedCandidateCountsList.append(numpy.zeros(bufferedImageList[i].shape, bufferedCandidateCounts.dtype))
                bufferedFrontCountsList.append(numpy.zeros(bufferedImageList[i].shape, bufferedFrontCounts.dtype))
                bufferedWindowStatusCodesList.append(numpy.zeros(bufferedImageList[i].shape, bufferedWindowStatusCodes.dtype))
                bufferedWindowStatusValuesList.append(numpy.zeros(bufferedImageList[i].shape, bufferedWindowStatusValues.dtype))

            # Import the threading module.                

            try:
                import threading as _threading
            except ImportError:
                import dummy_threading as _threading

            # Create and start the threads.

            threadList = []
            for i in range(threads):
                t = _threading.Thread(name='%i' % i, target=FrontsUtils.CayulaCornillonFronts, args=(bufferedImageList[i], bufferedMaskList[i], bufferedCandidateCountsList[i], bufferedFrontCountsList[i], bufferedWindowStatusCodesList[i], bufferedWindowStatusValuesList[i], bufferSize, histogramWindowSize, histogramWindowStride, minPropNonMaskedCells, minPopProp, minPopMeanDifference, minTheta, minSinglePopCohesion, minGlobalPopCohesion))
                t.setDaemon(True)
                print (' Debug: Starting thread %(id)s to process rows %(start)i to %(end)i.')
                threadList.append(t)

            for i in range(threads):
                threadList[i].start()

            # Wait for all of the threads to exit.

            while len(threadList) > 0:
                threadList[0].join()
                print (' Debug: Thread %(id)s exited.')
                del threadList[0]

            # Aggregate the arrays computed by the threads into the
            # array we will return to the caller.

            for i in range(threads - 1):
                bufferedCandidateCounts[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :] += bufferedCandidateCountsList[i][:,:]
                bufferedFrontCounts[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :] += bufferedFrontCountsList[i][:,:]
                bufferedWindowStatusCodes[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :] += bufferedWindowStatusCodesList[i][:,:]
                bufferedWindowStatusValues[i * blockHeight : (i+1) * blockHeight + bufferSize * 2, :] += bufferedWindowStatusValuesList[i][:,:]

            bufferedCandidateCounts[(i+1) * blockHeight : , :] += bufferedCandidateCountsList[i+1][:,:]
            bufferedFrontCounts[(i+1) * blockHeight : , :] += bufferedFrontCountsList[i+1][:,:]
            bufferedWindowStatusCodes[(i+1) * blockHeight : , :] += bufferedWindowStatusCodesList[i+1][:,:]
            bufferedWindowStatusValues[(i+1) * blockHeight : , :] += bufferedWindowStatusValuesList[i+1][:,:]

        print (' Debug: Histogram and cohesion algorithm complete. Elapsed time: %f seconds.')

        # If the caller specified that the edges should wrap,
        # CandidateCounts and FrontCounts for the the cells on the
        # left and right edges of the image are split between the
        # original locations of those cells and their duplicate
        # locations in the buffer strips along the opposite edges of
        # the image. Add the values from the buffer strips to the
        # values in the original locations. For example, if the
        # CandidateCounts array was 6x6 with a buffer of 2 and these
        # values:
        #
        #     [[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 4,  5,  0,  1,  2,  3,  4,  5,  0,  1],
        #      [10, 11,  6,  7,  8,  9, 10, 11,  6,  7],
        #      [16, 17, 12, 13, 14, 15, 16, 17, 12, 13],
        #      [22, 23, 18, 19, 20, 21, 22, 23, 18, 19],
        #      [28, 29, 24, 25, 26, 27, 28, 29, 24, 25],
        #      [34, 35, 30, 31, 32, 33, 34, 35, 30, 31],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]]
        #
        # The resulting array, after the copy operation, would be:
        #
        #     [[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 4,  5,  0,  2,  2,  3,  8, 10,  0,  1],
        #      [10, 11, 12, 14,  8,  9, 20, 22,  6,  7],
        #      [16, 17, 24, 26, 14, 15, 32, 34, 12, 13],
        #      [22, 23, 36, 38, 20, 21, 44, 46, 18, 19],
        #      [28, 29, 48, 50, 26, 27, 56, 58, 24, 25],
        #      [34, 35, 60, 62, 32, 33, 68, 70, 30, 31],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        #      [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]]

        if wrapEdges:
            bufferedCandidateCounts[bufferSize:bufferSize+image.shape[0], -(bufferSize*2):-bufferSize] += bufferedCandidateCounts[bufferSize:bufferSize+image.shape[0], 0:bufferSize]
            bufferedCandidateCounts[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize*2] += bufferedCandidateCounts[bufferSize:bufferSize+image.shape[0], -bufferSize:]
            bufferedFrontCounts[bufferSize:bufferSize+image.shape[0], -(bufferSize*2):-bufferSize] += bufferedFrontCounts[bufferSize:bufferSize+image.shape[0], 0:bufferSize]
            bufferedFrontCounts[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize*2] += bufferedFrontCounts[bufferSize:bufferSize+image.shape[0], -bufferSize:]

        # Return successfully.

        unbufferedImage = bufferedImage[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]
        unbufferedCandidateCounts = bufferedCandidateCounts[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]
        unbufferedFrontCounts = bufferedFrontCounts[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]
        unbufferedWindowStatusCodes = bufferedWindowStatusCodes[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]
        unbufferedWindowStatusValues = bufferedWindowStatusValues[bufferSize:bufferSize+image.shape[0], bufferSize:bufferSize+image.shape[1]]

        return copy.deepcopy(unbufferedMask), copy.deepcopy(unbufferedImage), copy.deepcopy(unbufferedCandidateCounts), copy.deepcopy(unbufferedFrontCounts), copy.deepcopy(unbufferedWindowStatusCodes), copy.deepcopy(unbufferedWindowStatusValues)


###############################################################################
# Names exported by this module
###############################################################################

#__all__ = ['CayulaCornillonEdgeDetection']

###############################################################################
# Driver
###############################################################################
#____

def Usage(message):
    print (message)
    print ('Usage:\t Fronts.py -threads nthreads imagename')
    sys.exit(1)

if __name__=="__main__":

    # Arguments initialization
    histogramWindowStride = None
    minTheta = None
    minPopProp = None
    minPopMeanDifference = None
    minSinglePopCohesion = None
    histogramWindowSize = None
    minImageValue=None
    rid = ''
    outfrontfile = ' '

    # Reads the arguments
    ii=1
    while ii <len(sys.argv):

        arg = sys.argv[ii]
        if arg == '-threads':
            ii = ii + 1
            threads=float(sys.argv[ii])
        if arg == '-stride':
            ii = ii + 1
            histogramWindowStride=int(sys.argv[ii])
        if arg == '-minTheta':
            ii = ii + 1
            minTheta=float(sys.argv[ii])
        if arg == '-windowsize':
            ii = ii + 1
            histogramWindowSize=int(sys.argv[ii])
        if arg == '-outfrontfile':
            ii = ii + 1
            outfrontfile=sys.argv[ii]
        if arg == '-minPopProp':
            ii = ii + 1
            minPopProp=float(sys.argv[ii])
        if arg == '-minPopMeanDifference':
            ii = ii + 1
            minPopMeanDifference=float(sys.argv[ii])
        if arg == '-minSinglePopCohesion':
            ii = ii + 1
            minSinglePopCohesion=float(sys.argv[ii])
        if arg == '-minImageValue':
            ii = ii + 1
            minImageValue=float(sys.argv[ii])
        if arg == '-date':
            ii = ii + 1
            date=sys.argv[ii]
	else:
	    inFile=sys.argv[ii]
	    ii = ii + 1	

    # Load the image from file
    print ('Load image')

    fid = gdal.Open(inFile, GA_ReadOnly) 
    inband = fid.GetRasterBand(1)
    inData = inband.ReadAsArray(0,0,inband.XSize,inband.YSize)
    print (inData.shape[0])
    print (inData.shape[1])
    inDataInt = Numeric.uint16(inData*1000)
    
    # Call FrontDetection Algorithm
    print ('Call algo')
    [uMask, uImage, uCandidateCounts, uFrontCounts,uWindowStatusCodes, uWindowStatusValues] = DetectEdgesInSingleImage(inDataInt,histogramWindowStride,minTheta,histogramWindowSize,minPopProp, minPopMeanDifference,minSinglePopCohesion,minImageValue)

    # Write the results to a Geotiff image
   
    # get infos from the first file
    nb = fid.RasterCount
    ns = fid.RasterXSize
    nl = fid.RasterYSize

    dataType = fid.GetRasterBand(1).DataType
    geoTransform = fid.GetGeoTransform()
    projection = fid.GetProjection()

    # instantiate output(s)
    # Initialise other parameters
    format = 'GTiff'
    options=[]
    options.append('compress=lzw')

    # Generate output file for detected fronts uFrontCounts
    #outfile = outdir + date + rid
    print ('Front file')
    print (outfrontfile)

    outDrv = gdal.GetDriverByName(format)

    outDS = outDrv.Create(outfrontfile, ns, nl, nb, dataType,options)
    outDS.SetGeoTransform(geoTransform)
    outDS.SetProjection(projection)

    outband = outDS.GetRasterBand(1)
    outband.WriteArray(uFrontCounts,0,0)

###-TO REMOVE

    # Generate output file for unbufferedMask
    #outfile = outdir + date + '_outuMask'+rid
    
    #outDS = outDrv.Create(outfile, ns, nl, nb, dataType,options)
    #outDS.SetGeoTransform(geoTransform)
    #outDS.SetProjection(projection)    
   
    #outband = outDS.GetRasterBand(1)
    #outband.WriteArray(uMask,0,0)

 # Generate output file for unbufferedImage
    #outfile = outdir + date + '_outuImage'+rid

    #outDS = outDrv.Create(outfile, ns, nl, nb, dataType,options)
    #outDS.SetGeoTransform(geoTransform)
    #outDS.SetProjection(projection)    

    #outband = outDS.GetRasterBand(1)
    #outband.WriteArray(uImage,0,0)

 # Generate output file for unbufferedCandidateCounts
    #outfile = outdir + date + '_outuCandidateCounts'+rid

    #outDS = outDrv.Create(outfile, ns, nl, nb, dataType,options)
    #outDS.SetGeoTransform(geoTransform)
    #outDS.SetProjection(projection)    

    #outband = outDS.GetRasterBand(1)
    #outband.WriteArray(uCandidateCounts,0,0)   

# Generate output file for uFrontCounts
    #outfile = outdir + date + '_outFrontCounts'+rid

    #outDS = outDrv.Create(outfile, ns, nl, nb, dataType,options)
    #outDS.SetGeoTransform(geoTransform)
    #outDS.SetProjection(projection)

    #outband = outDS.GetRasterBand(1)
    #outband.WriteArray(uFrontCounts,0,0)

# Generate output file for unbufferedWindowStatusCodes
    #outfile = outdir + date + '_outuWindowStatusCodes'+rid

    #outDS = outDrv.Create(outfile, ns, nl, nb, dataType,options)
    #outDS.SetGeoTransform(geoTransform)
    #outDS.SetProjection(projection)    

    #outband = outDS.GetRasterBand(1)
    #outband.WriteArray(uWindowStatusCodes,0,0)   


# Generate output file for unbufferedWindowStatusValues
    #outfile = outdir + date + '_outuWindowStatusValues'+rid

    #outDS = outDrv.Create(outfile, ns, nl, nb, dataType,options)
    #outDS.SetGeoTransform(geoTransform)
    #outDS.SetProjection(projection)

    #outband = outDS.GetRasterBand(1)
    #outband.WriteArray(uWindowStatusValues,0,0)

