// FrontsUtils.cpp - Implements portions of front-detection algorithms that are
// too performance-sensitive to implement in Python. Not intended to be called
// directly -- call wrapper routines in Fronts.py instead.
//
// Copyright (C) 2007 Jason J. Roberts
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License (available in the file LICENSE.TXT)
// for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

//#include "/usr/include/python2.7/Python.h"
//#include "/usr/include/python2.7/pyconfig.h"
//#include "/usr/share/pyshared/numpy/core/include/numpy/arrayobject.h"
#define PY_SSIZE_T_CLEAN
//#include "/usr/include/python3.6/Python.h"
//#include "/usr/include/python3.6/pyconfig.h"
//#include "/usr/local/lib/python3.6/dist-packages/numpy/core/include/numpy/arrayobject.h"
#include "/opt/conda/include/python3.7m/Python.h"
#include "/opt/conda/include/python3.7m/pyconfig.h"
#include "/opt/conda/lib/python3.7/site-packages/numpy/core/include/numpy/arrayobject.h"

#pragma warning(disable: 4244)		// warning C4244: '=' : conversion from 'double' to 'npy_float32', possible loss of data

/*
 *  This Quickselect routine is based on the algorithm described in
 *  "Numerical recipes in C", Second Edition,
 *  Cambridge University Press, 1992, Section 8.5, ISBN 0-521-43108-5
 *  The original code by Nicolas Devillard - 1998. Public domain.
 *  Converted to C macros by Jason Roberts.
 */
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define ELEM_SWAP(dataType, a,b) { register dataType t=(a);(a)=(b);(b)=t; }

#define QUICK_MEDIAN_SELECT(dataType, arr, n, pFilteredImage, row, col)                 \
{                                                                                       \
    int low, high ;                                                                     \
    int median;                                                                         \
    int middle, ll, hh;                                                                 \
                                                                                        \
    low = 0 ; high = n-1 ; median = (low + high) / 2;                                   \
    for (;;) {                                                                          \
        if (high <= low) /* One element only */                                         \
        {                                                                               \
            *((dataType *)PyArray_GETPTR2(pFilteredImage, row, col)) = arr[median] ;    \
            break;                                                                      \
        }                                                                               \
                                                                                        \
        if (high == low + 1) {  /* Two elements only */                                 \
            if (arr[low] > arr[high])                                                   \
                ELEM_SWAP(dataType, arr[low], arr[high]) ;                              \
            *((dataType *)PyArray_GETPTR2(pFilteredImage, row, col)) = arr[median] ;    \
            break;                                                                      \
        }                                                                               \
                                                                                        \
        /* Find median of low, middle and high items; swap into position low */         \
        middle = (low + high) / 2;                                                      \
        if (arr[middle] > arr[high])    ELEM_SWAP(dataType, arr[middle], arr[high]) ;   \
        if (arr[low] > arr[high])       ELEM_SWAP(dataType, arr[low], arr[high]) ;      \
        if (arr[middle] > arr[low])     ELEM_SWAP(dataType, arr[middle], arr[low]) ;    \
                                                                                        \
        /* Swap low item (now in position middle) into position (low+1) */              \
        ELEM_SWAP(dataType, arr[middle], arr[low+1]) ;                                  \
                                                                                        \
        /* Nibble from each end towards middle, swapping items when stuck */            \
        ll = low + 1;                                                                   \
        hh = high;                                                                      \
        for (;;) {                                                                      \
            do ll++; while (arr[low] > arr[ll]) ;                                       \
            do hh--; while (arr[hh]  > arr[low]) ;                                      \
                                                                                        \
            if (hh < ll)                                                                \
                break;                                                                  \
                                                                                        \
            ELEM_SWAP(dataType, arr[ll], arr[hh]) ;                                     \
        }                                                                               \
                                                                                        \
        /* Swap middle item (in position low) back into correct position */             \
        ELEM_SWAP(dataType, arr[low], arr[hh]) ;                                        \
                                                                                        \
        /* Re-set active partition */                                                   \
        if (hh <= median)                                                               \
            low = ll;                                                                   \
        if (hh >= median)                                                               \
            high = hh - 1;                                                              \
    }                                                                                   \
}

#define MEDIAN_FILTER(dataType, pBufferedImage, pBufferedMask, pFilteredImage, bufferSize, medianFilterWindowSize)          \
{                                                                                                                           \
    /* Allocate a temporary 1D array to hold the non-masked values of a window. */                                          \
                                                                                                                            \
    dataType *pTempArray = (dataType *)PyMem_Malloc(medianFilterWindowSize * medianFilterWindowSize * sizeof(dataType));    \
    if (pTempArray == NULL)                                                                                                 \
    {                                                                                                                       \
        PyErr_SetString(PyExc_MemoryError, "out of memory");                                                                \
        Py_XDECREF(pFilteredImage);                                                                                         \
        return NULL;                                                                                                        \
    }                                                                                                                       \
                                                                                                                            \
    /* Pass the window over pBufferedImage, calculating the median for all */                                               \
    /* non-masked cells and storing it in pFilteredImage.                  */                                               \
                                                                                                                            \
    int halfWindowSize = medianFilterWindowSize >> 1;                                                                       \
    for (int row = bufferSize; row < PyArray_DIM(pBufferedMask, 0) - bufferSize; row++)                                     \
        for (int col = bufferSize; col < PyArray_DIM(pBufferedMask, 1) - bufferSize; col++)                                 \
            if (!*((npy_bool *)PyArray_GETPTR2(pBufferedMask, row, col)))                                                   \
            {                                                                                                               \
                /* This cell is not masked. Copy all of the non-masked cells in */                                          \
                /* the surrounding window to the temporary array.               */                                          \
                                                                                                                            \
                int numValues = 0;                                                                                          \
                for (int i = row - halfWindowSize; i <= row + halfWindowSize; i++)                                          \
                    for (int j = col - halfWindowSize; j <= col + halfWindowSize; j++)                                      \
                        if (!*((npy_bool *)PyArray_GETPTR2(pBufferedMask, i, j)))                                           \
                        {                                                                                                   \
                            pTempArray[numValues] = *((dataType *)PyArray_GETPTR2(pBufferedImage, i, j));                   \
                            numValues++;                                                                                    \
                        }                                                                                                   \
                                                                                                                            \
                /* Select the median value of the temporary array and store it */                                           \
                /* in pFilteredImage.                                          */                                           \
                                                                                                                            \
                QUICK_MEDIAN_SELECT(dataType, pTempArray, numValues, pFilteredImage, row, col);                             \
            }                                                                                                               \
                                                                                                                            \
    /* Free the temporary array. */                                                                                         \
                                                                                                                            \
    PyMem_Free(pTempArray);                                                                                                 \
}

static PyObject *MedianFilter(PyObject *self, PyObject *args)
{
    // Parse arguments.

    PyArrayObject *pBufferedImage = NULL;
    PyArrayObject *pBufferedMask = NULL;
    int bufferSize = 0;
    int medianFilterWindowSize = 0;

    if (!PyArg_ParseTuple(args, "O!O!ii", &PyArray_Type, &pBufferedImage, &PyArray_Type, &pBufferedMask, &bufferSize, &medianFilterWindowSize))
        return NULL;

    // Allocate an array to return.

    PyArrayObject *pFilteredImage = (PyArrayObject *) PyArray_Copy(pBufferedImage);
    if (pFilteredImage == NULL)
        return NULL;

    // Compute the median for every cell that is not masked.

    switch (PyArray_TYPE(pBufferedImage))
    {
        case NPY_INT8:
            MEDIAN_FILTER(npy_int8, pBufferedImage, pBufferedMask, pFilteredImage, bufferSize, medianFilterWindowSize);
            break;

        case NPY_UINT8:
            MEDIAN_FILTER(npy_uint8, pBufferedImage, pBufferedMask, pFilteredImage, bufferSize, medianFilterWindowSize);
            break;

        case NPY_INT16:
            MEDIAN_FILTER(npy_int16, pBufferedImage, pBufferedMask, pFilteredImage, bufferSize, medianFilterWindowSize);
            break;

        case NPY_UINT16:
            MEDIAN_FILTER(npy_uint16, pBufferedImage, pBufferedMask, pFilteredImage, bufferSize, medianFilterWindowSize);
            break;
    }

    // Return successfully.

    return (PyObject *)pFilteredImage;
}

static PyObject *FocalSumOfMask(PyObject *self, PyObject *args)
{
    // Parse arguments.

    PyArrayObject *pBufferedMask = NULL;
    int bufferSize = 0;
    int windowSize = 0;

    if (!PyArg_ParseTuple(args, "O!ii", &PyArray_Type, &pBufferedMask, &bufferSize, &windowSize))
        return NULL;

    // Allocate an array to return.

    PyArrayObject *pSum = (PyArrayObject *) PyArray_ZEROS(2, PyArray_DIMS(pBufferedMask), NPY_UINT8, 0);
    if (pSum == NULL)
        return NULL;

    // Compute the focal sum for every masked cell.

    int halfWindowSize = windowSize >> 1;
    for (int row = bufferSize; row < PyArray_DIM(pBufferedMask, 0) - bufferSize; row++)
        for (int col = bufferSize; col < PyArray_DIM(pBufferedMask, 1) - bufferSize; col++)
            if (*((npy_bool *)PyArray_GETPTR2(pBufferedMask, row, col)))
            {
                npy_uint8 sum = 0;

                for (int i = row - halfWindowSize; i <= row + halfWindowSize; i++)
                    for (int j = col - halfWindowSize; j <= col + halfWindowSize; j++)
                        if (*((npy_bool *)PyArray_GETPTR2(pBufferedMask, i, j)))
                            sum++;

                *((npy_uint8 *)PyArray_GETPTR2(pSum, row, col)) = sum;
            }

    // Return successfully.

    return (PyObject *)pSum;
}

// Window status codes.

#define WS_TOO_FEW_UNMASKED_CELLS        1
#define WS_SMALL_POP_TOO_SMALL           2
#define WS_POP_MEAN_DIFF_TOO_SMALL       3
#define WS_CRITERION_FUNC_TOO_SMALL      4
#define WS_SINGLE_POP_COHESION_TOO_SMALL 5
#define WS_GLOBAL_POP_COHESION_TOO_SMALL 6
#define WS_FOUND_FRONT                   7

#define CAYULA_CORNILLON_FRONTS(pBufferedImage, pBufferedMask, pBufferedCandidateCounts, pBufferedFrontCounts, pBufferedWindowStatusCodes, pBufferedWindowStatusValues, bufferSize, histogramWindowSize, histogramWindowStride, minPropNonMaskedCells, minPopProp, minPopMeanDifference, minTheta, minSinglePopCohesion, minGlobalPopCohesion, dataType, dataTypeMin, dataTypeMax) \
{                                                                                                                   \
    /* Initialize some values used in the algorithm. */                                                             \
                                                                                                                    \
    int minNonMaskedCells = (int)((double)histogramWindowSize * (double)histogramWindowSize * minPropNonMaskedCells); \
    npy_uint16 valueCounts[dataTypeMax - (dataTypeMin) + 1];   /* Number of times this value occurred in the window (i.e. a histogram for the window).*/ \
    memset(valueCounts, 0, sizeof(valueCounts));                                                                    \
                                                                                                                    \
    /* Pass the window over pBufferedImage. */                                                                      \
                                                                                                                    \
    for (int row = bufferSize; row < PyArray_DIM(pBufferedMask, 0) - bufferSize; row += histogramWindowStride)      \
        for (int col = bufferSize; col < PyArray_DIM(pBufferedMask, 1) - bufferSize; col += histogramWindowStride)  \
        {                                                                                                           \
            /***** BEGIN HISTOGRAM ALGORITHM *****/                                                                 \
                                                                                                                    \
            /* Walk through the non-masked cells in the window. These are the */                                    \
            /* only cells that will be considered by the algorithm.           */                                    \
                                                                                                                    \
            int wStartRow = row - (histogramWindowSize >> 1);                                                       \
            int wStartCol = col - (histogramWindowSize >> 1);                                                       \
            int totalCount = 0;                                                                                     \
            double totalSum = 0;                                                                                    \
            double totalSumSquares = 0;                                                                             \
            dataType wMax = dataTypeMin;                                                                            \
            dataType wMin = dataTypeMax;                                                                            \
                                                                                                                    \
            for (int wRow = wStartRow; wRow < wStartRow + histogramWindowSize; wRow++)                              \
                for (int wCol = wStartCol; wCol < wStartCol + histogramWindowSize; wCol++)                          \
                    if (!*((npy_bool *)PyArray_GETPTR2(pBufferedMask, wRow, wCol)))                                 \
                    {                                                                                               \
                        /* Obtain the value of this cell and increment the count */                                 \
                        /* of occurrances of this value (this is the histogram). */                                 \
                                                                                                                    \
                        dataType value = *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow, wCol));                \
                        valueCounts[(int)value - (dataTypeMin)]++;                                                  \
                                                                                                                    \
                        /* Record the minimum and maximum values we find in the   */                                \
                        /* window. We use these as the lower and upper bounds of  */                                \
                        /* the histogram, and ignore the segments below the min   */                                \
                        /* and above the max in later processing, for efficiency. */                                \
                                                                                                                    \
                        if (value > wMax)                                                                           \
                            wMax = value;                                                                           \
                        if (value < wMin)                                                                           \
                            wMin = value;                                                                           \
                                                                                                                    \
                        /* Increment the total count of cells in the window. */                                     \
                                                                                                                    \
                        totalCount++;                                                                               \
                                                                                                                    \
                        /* Add the value to the total sum and sum of squares for */                                 \
                        /* the window.                                           */                                 \
                                                                                                                    \
                        totalSum += (double)value;                                                                  \
                        totalSumSquares += (double)value * (double)value;                                           \
                    }                                                                                               \
                                                                                                                    \
            /* If the total count of non-masked cells in this window does not */                                    \
            /* meet the minimum threshold for sufficient statistical power,   */                                    \
            /* proceed to the next window.                                    */                                    \
                                                                                                                    \
            if (totalCount < minNonMaskedCells)                                                                     \
            {                                                                                                       \
                if (totalCount > 0)                                                                                 \
                    memset(valueCounts + (int)wMin - (dataTypeMin), 0, ((int)wMax - (int)wMin + 1) * sizeof(npy_uint16)); \
                *((npy_int8 *)PyArray_GETPTR2(pBufferedWindowStatusCodes, row, col)) = WS_TOO_FEW_UNMASKED_CELLS;   \
                *((npy_float32 *)PyArray_GETPTR2(pBufferedWindowStatusValues, row, col)) = (float)totalCount / ((float)histogramWindowSize * (float)histogramWindowSize); \
                continue;                                                                                           \
            }                                                                                                       \
                                                                                                                    \
            /* The cells in this window are candidates for containing a front. */                                   \
            /* Increment their candidate counts.                               */                                   \
                                                                                                                    \
            for (int wRow = wStartRow; wRow < wStartRow + histogramWindowSize; wRow++)                              \
                for (int wCol = wStartCol; wCol < wStartCol + histogramWindowSize; wCol++)                          \
                    if (!*((npy_bool *)PyArray_GETPTR2(pBufferedMask, wRow, wCol)))                                 \
                        *((npy_int16 *)PyArray_GETPTR2(pBufferedCandidateCounts, wRow, wCol)) += 1;                 \
                                                                                                                    \
            /* Iterate through the histogram, using each value to separate the   */                                 \
            /* histogram into two populations, A and B, where A consists of the  */                                 \
            /* cells <= to the threshold value and B consists of the cells > the */                                 \
            /* threshold value. Find the threshold value that maximizes the      */                                 \
            /* separation of the means of populations A and B. In theory, we     */                                 \
            /* should be finding the value that maximizes the "between cluster   */                                 \
            /* variance", Jb(tau), equation 11 in the Cayula Cornillon 1992      */                                 \
            /* paper. But notice that the (N1 + N2)^2 term is missing from the   */                                 \
            /* calculation of the "separation" variable. I copied this           */                                 \
            /* implementation from rational fortran code provided by Dave        */                                 \
            /* Ullman, originally written by Cayula. I cannot explain why his    */                                 \
            /* code differed from the paper.                                     */                                 \
                                                                                                                    \
            int popACount = 0;                                                                                      \
            double popASum = 0;                                                                                     \
            dataType thresholdValue = dataTypeMin;                                                                  \
            int thresholdPopACount = 0;                                                                             \
            double thresholdSeparation = -1;                                                                        \
            double thresholdPopAMean = 0;                                                                           \
            double thresholdPopBMean = 0;                                                                           \
                                                                                                                    \
            for (int i = (int)wMin - (dataTypeMin); i <= (int)wMax - (dataTypeMin); i++)                            \
            {                                                                                                       \
                if (valueCounts[i] > 0)                                                                             \
                {                                                                                                   \
                    popACount += valueCounts[i];                                                                    \
                    popASum += (double)valueCounts[i] * (double)(i + (dataTypeMin));                                \
                                                                                                                    \
                    if (popACount < totalCount)                                                                     \
                    {                                                                                               \
                        int popBCount = totalCount - popACount;                                                     \
                        double popBSum = totalSum - popASum;                                                        \
                        double popAMean = popASum / (double)popACount;                                              \
                        double popBMean = popBSum / (double)popBCount;                                              \
                        double separation = (double)popACount * (double)popBCount * (popAMean - popBMean) * (popAMean - popBMean); \
                        if (separation > thresholdSeparation)                                                       \
                        {                                                                                           \
                            thresholdSeparation = separation;                                                       \
                            thresholdValue = (dataType)(i + (dataTypeMin));                                         \
                            thresholdPopACount = popACount;                                                         \
                            thresholdPopAMean = popAMean;                                                           \
                            thresholdPopBMean = popBMean;                                                           \
                        }                                                                                           \
                    }                                                                                               \
                }                                                                                                   \
            }                                                                                                       \
                                                                                                                    \
            /* Zero out the histogram counts in preparation for the next window. */                                 \
                                                                                                                    \
            memset(valueCounts + (int)wMin - (dataTypeMin), 0, ((int)wMax - (int)wMin + 1) * sizeof(npy_uint16));   \
                                                                                                                    \
            /* Only continue with this window if the proportional size of the    */                                 \
            /* smaller population exceeds the minimum allowed value. This test   */                                 \
            /* corresponds to equation 14 in the Cayula-Cornillon 1992 paper and */                                 \
            /* is present in the fortran code I obtained from Dave Ullman.       */                                 \
                                                                                                                    \
            if (thresholdValue == dataTypeMin)    /* I'm not sure this can actually happen */                       \
            {                                                                                                       \
                *((npy_int8 *)PyArray_GETPTR2(pBufferedWindowStatusCodes, row, col)) = WS_SMALL_POP_TOO_SMALL;      \
                *((npy_float32 *)PyArray_GETPTR2(pBufferedWindowStatusValues, row, col)) = 0;                       \
                continue;                                                                                           \
            }                                                                                                       \
                                                                                                                    \
            if ((double)thresholdPopACount / (double)totalCount < minPopProp)                                       \
            {                                                                                                       \
                *((npy_int8 *)PyArray_GETPTR2(pBufferedWindowStatusCodes, row, col)) = WS_SMALL_POP_TOO_SMALL;      \
                *((npy_float32 *)PyArray_GETPTR2(pBufferedWindowStatusValues, row, col)) = (float)thresholdPopACount / (float)totalCount; \
                continue;                                                                                           \
            }                                                                                                       \
                                                                                                                    \
            if (1.0 - (double)thresholdPopACount / (double)totalCount < minPopProp)                                 \
            {                                                                                                       \
                *((npy_int8 *)PyArray_GETPTR2(pBufferedWindowStatusCodes, row, col)) = WS_SMALL_POP_TOO_SMALL;      \
                *((npy_float32 *)PyArray_GETPTR2(pBufferedWindowStatusValues, row, col)) = 1.0 - (float)thresholdPopACount / (float)totalCount; \
                continue;                                                                                           \
            }                                                                                                       \
                                                                                                                    \
            /* Also abort this window if the difference in the populations'      */                                 \
            /* means is less than a minimum value. The fortran code said that "a */                                 \
            /* temperature difference of less than 3 digital count between 2     */                                 \
            /* populations [is] likely to be a result of the discrete nature of  */                                 \
            /* the data."                                                        */                                 \
                                                                                                                    \
            if (thresholdPopBMean - thresholdPopAMean < minPopMeanDifference)                                       \
            {                                                                                                       \
                *((npy_int8 *)PyArray_GETPTR2(pBufferedWindowStatusCodes, row, col)) = WS_POP_MEAN_DIFF_TOO_SMALL;  \
                *((npy_float32 *)PyArray_GETPTR2(pBufferedWindowStatusValues, row, col)) = (float)(thresholdPopBMean - thresholdPopAMean); \
                continue;                                                                                           \
            }                                                                                                       \
                                                                                                                    \
            /* Calculate the criterion function for the window. I believe this  */                                  \
            /* is THETA(TAUopt) discussed on page 72 of the paper. I copied the */                                  \
            /* code from Dave Ullman's fortran code, but as before, I don't     */                                  \
            /* understand the computations. */                                                                      \
                                                                                                                    \
            double totalMean = totalSum / (double) totalCount;                                                      \
            double variance = totalSumSquares - (totalMean * totalMean * totalCount);                               \
            double theta = 0;                                                                                       \
            if (variance != 0)                                                                                      \
                theta = thresholdSeparation / (variance * (double) totalCount);                                     \
                                                                                                                    \
            /* Only continue with this window if the criterion function meets or */                                 \
            /* exceeds the minimum value.                                        */                                 \
                                                                                                                    \
            if (theta < minTheta)                                                                                   \
            {                                                                                                       \
                *((npy_int8 *)PyArray_GETPTR2(pBufferedWindowStatusCodes, row, col)) = WS_CRITERION_FUNC_TOO_SMALL; \
                *((npy_float32 *)PyArray_GETPTR2(pBufferedWindowStatusValues, row, col)) = (float)theta;            \
                continue;                                                                                           \
            }                                                                                                       \
                                                                                                                    \
            /***** END HISTOGRAM ALGORITHM *****/                                                                   \
                                                                                                                    \
            /***** BEGIN COHESION ALGORITHM *****/                                                                  \
                                                                                                                    \
            /* Count the number of times a population A cell is immediately      */                                 \
            /* adjacent to another population A cell, and the same for           */                                 \
            /* population B. A cell can be adjacent on four sides. Count only    */                                 \
            /* two of them (bottom and right side) because doing all four would  */                                 \
            /* be redundant. Do not count diagonal neighbors.                    */                                 \
                                                                                                                    \
            /* I could not fully understand the algorithm implemented in the     */                                 \
            /* fortran code from Dave Ullman. I am not confident it implemented  */                                 \
            /* what was described in the Cayula Cornillion 1992 paper. It        */                                 \
            /* appeared to only factor in vertical neighbors to the cohesion     */                                 \
            /* coefficient calculation. The matlab algorithm implemented by      */                                 \
            /* Alistair Hobday appeared to only examine horizontal neighbors. My */                                 \
            /* algorithm looks at both, as described in the 1992 paper.          */                                 \
                                                                                                                    \
            int countANextToA = 0;                                                                                  \
            int countBNextToB = 0;                                                                                  \
            int countANextToAOrB = 0;                                                                               \
            int countBNextToAOrB = 0;                                                                               \
            for (int wRow = wStartRow; wRow < wStartRow + histogramWindowSize; wRow++)                              \
                for (int wCol = wStartCol; wCol < wStartCol + histogramWindowSize; wCol++)                          \
                    if (!*((npy_bool *)PyArray_GETPTR2(pBufferedMask, wRow, wCol)))                                 \
                    {                                                                                               \
                        dataType value = *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow, wCol));                \
                                                                                                                    \
                        /* Examine the bottom neighbor unless we are on the last */                                 \
                        /* row (we do not examine cells outside the window) or   */                                 \
                        /* it is masked.                                         */                                 \
                                                                                                                    \
                        if (wRow < wStartRow + histogramWindowSize - 1 && !*((npy_bool *)PyArray_GETPTR2(pBufferedMask, wRow + 1, wCol))) \
                            if (value <= thresholdValue)                                                            \
                            {                                                                                       \
                                countANextToAOrB++;                                                                 \
                                if (*((dataType *)PyArray_GETPTR2(pBufferedImage, wRow + 1, wCol)) <= thresholdValue) \
                                    countANextToA++;                                                                \
                            }                                                                                       \
                            else                                                                                    \
                            {                                                                                       \
                                countBNextToAOrB++;                                                                 \
                                if (*((dataType *)PyArray_GETPTR2(pBufferedImage, wRow + 1, wCol)) > thresholdValue) \
                                    countBNextToB++;                                                                \
                            }                                                                                       \
                                                                                                                    \
                        /* Examine the right neighbor unless we are on the last */                                  \
                        /* column (we do not examine cells outside the window)  */                                  \
                        /* or it is masked.                                     */                                  \
                                                                                                                    \
                        if (wCol < wStartCol + histogramWindowSize - 1 && !*((npy_bool *)PyArray_GETPTR2(pBufferedMask, wRow, wCol + 1))) \
                            if (value <= thresholdValue)                                                            \
                            {                                                                                       \
                                countANextToAOrB++;                                                                 \
                                if (*((dataType *)PyArray_GETPTR2(pBufferedImage, wRow, wCol + 1)) <= thresholdValue) \
                                    countANextToA++;                                                                \
                            }                                                                                       \
                            else                                                                                    \
                            {                                                                                       \
                                countBNextToAOrB++;                                                                 \
                                if (*((dataType *)PyArray_GETPTR2(pBufferedImage, wRow, wCol + 1)) > thresholdValue)\
                                    countBNextToB++;                                                                \
                            }                                                                                       \
                    }                                                                                               \
                                                                                                                    \
            /* Calculate the cohesion coefficients. */                                                              \
                                                                                                                    \
            double popACohesion = (double)countANextToA / (double)countANextToAOrB;                                 \
            double popBCohesion = (double)countBNextToB / (double)countBNextToAOrB;                                 \
            double globalCohesion = (double)(countANextToA + countBNextToB) / (double)(countANextToAOrB + countBNextToAOrB); \
                                                                                                                    \
            /* Only continue with this window if the cohesion coefficients meet */                                  \
            /* the minimum values.                                              */                                  \
                                                                                                                    \
            if (popACohesion < minSinglePopCohesion)                                                                \
            {                                                                                                       \
                *((npy_int8 *)PyArray_GETPTR2(pBufferedWindowStatusCodes, row, col)) = WS_SINGLE_POP_COHESION_TOO_SMALL; \
                *((npy_float32 *)PyArray_GETPTR2(pBufferedWindowStatusValues, row, col)) = (float)popACohesion;     \
                continue;                                                                                           \
            }                                                                                                       \
                                                                                                                    \
            if (popBCohesion < minSinglePopCohesion)                                                                \
            {                                                                                                       \
                *((npy_int8 *)PyArray_GETPTR2(pBufferedWindowStatusCodes, row, col)) = WS_SINGLE_POP_COHESION_TOO_SMALL; \
                *((npy_float32 *)PyArray_GETPTR2(pBufferedWindowStatusValues, row, col)) = (float)popBCohesion;     \
                continue;                                                                                           \
            }                                                                                                       \
                                                                                                                    \
            if (globalCohesion < minGlobalPopCohesion)                                                              \
            {                                                                                                       \
                *((npy_int8 *)PyArray_GETPTR2(pBufferedWindowStatusCodes, row, col)) = WS_GLOBAL_POP_COHESION_TOO_SMALL; \
                *((npy_float32 *)PyArray_GETPTR2(pBufferedWindowStatusValues, row, col)) = (float)globalCohesion;   \
                continue;                                                                                           \
            }                                                                                                       \
                                                                                                                    \
            /***** END COHESION ALGORITHM *****/                                                                    \
                                                                                                                    \
            /* If we got to here, this window contains a front. */                                                  \
                                                                                                                    \
            *((npy_int8 *)PyArray_GETPTR2(pBufferedWindowStatusCodes, row, col)) = WS_FOUND_FRONT;                  \
                                                                                                                    \
            for (int wRow = wStartRow; wRow < wStartRow + histogramWindowSize; wRow++)                              \
                for (int wCol = wStartCol; wCol < wStartCol + histogramWindowSize; wCol++)                          \
                    if (!*((npy_bool *)PyArray_GETPTR2(pBufferedMask, wRow, wCol)))                                 \
                    {                                                                                               \
                        dataType value = *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow, wCol));                \
                                                                                                                    \
                        /* If either the bottom, right, top, or left nighbors   */                                  \
                        /* within this window is in the opposite population as  */                                  \
                        /* the current cell, then both that cell and this one   */                                  \
                        /* are along the front. Increment the front count for   */                                  \
                        /* the current cell. The neighbors will be marked when  */                                  \
                        /* we get to them in the loop.                          */                                  \
                                                                                                                    \
                        /* Note that this differs from the original fortran     */                                  \
                        /* code provided by Dave Ullman. That code only         */                                  \
                        /* considered the bottom and right neighbors,           */                                  \
                        /* presumably because the countour-following code that  */                                  \
                        /* was called later expected the fronts to be only one  */                                  \
                        /* cell wide. Because I did not implement the countour  */                                  \
                        /* following code, or even thinning code, I am leaving  */                                  \
                        /* it up to the caller to decide the appropriate method */                                  \
                        /* for thinning and extending the fronts, if desired.   */                                  \
                                                                                                                    \
                        if ((wRow < wStartRow + histogramWindowSize - 1 && !*((npy_bool *)PyArray_GETPTR2(pBufferedMask, wRow + 1, wCol)) &&  \
                             (value <= thresholdValue && *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow + 1, wCol)) > thresholdValue ||   \
                              value > thresholdValue && *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow + 1, wCol)) <= thresholdValue)) || \
                                                                                                                                              \
                            (wCol < wStartCol + histogramWindowSize - 1 && !*((npy_bool *)PyArray_GETPTR2(pBufferedMask, wRow, wCol + 1)) &&  \
                             (value <= thresholdValue && *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow, wCol + 1)) > thresholdValue ||   \
                              value > thresholdValue && *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow, wCol + 1)) <= thresholdValue)) || \
                                                                                                                                              \
                            (wRow > wStartRow && !*((npy_bool *)PyArray_GETPTR2(pBufferedMask, wRow - 1, wCol)) &&                            \
                             (value <= thresholdValue && *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow - 1, wCol)) > thresholdValue ||   \
                              value > thresholdValue && *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow - 1, wCol)) <= thresholdValue)) || \
                                                                                                                                              \
                            (wCol > wStartCol && !*((npy_bool *)PyArray_GETPTR2(pBufferedMask, wRow, wCol - 1)) &&                            \
                             (value <= thresholdValue && *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow, wCol - 1)) > thresholdValue ||   \
                              value > thresholdValue && *((dataType *)PyArray_GETPTR2(pBufferedImage, wRow, wCol - 1)) <= thresholdValue)))   \
                                                                                                                    \
                            *((npy_int16 *)PyArray_GETPTR2(pBufferedFrontCounts, wRow, wCol)) += 1;                 \
                    }                                                                                               \
        }                                                                                                           \
}

static PyObject *CayulaCornillonFronts(PyObject *self, PyObject *args)
{
    // Parse arguments.

    PyArrayObject *pBufferedImage = NULL;
    PyArrayObject *pBufferedMask = NULL;
    PyArrayObject *pBufferedCandidateCounts = NULL;
    PyArrayObject *pBufferedFrontCounts = NULL;
    PyArrayObject *pBufferedWindowStatusCodes = NULL;
    PyArrayObject *pBufferedWindowStatusValues = NULL;
    int bufferSize = 0;
    int histogramWindowSize = 0;
    int histogramWindowStride = 0;
    double minPropNonMaskedCells = 0;
    double minPopProp = 0;
    double minPopMeanDifference = 0;
    double minTheta = 0;
    double minSinglePopCohesion = 0;
    double minGlobalPopCohesion = 0;

    if (!PyArg_ParseTuple(args, "O!O!O!O!O!O!iiidddddd", &PyArray_Type, &pBufferedImage, &PyArray_Type, &pBufferedMask, &PyArray_Type, &pBufferedCandidateCounts, &PyArray_Type, &pBufferedFrontCounts, &PyArray_Type, &pBufferedWindowStatusCodes, &PyArray_Type, &pBufferedWindowStatusValues, &bufferSize, &histogramWindowSize, &histogramWindowStride, &minPropNonMaskedCells, &minPopProp, &minPopMeanDifference, &minTheta, &minSinglePopCohesion, &minGlobalPopCohesion))
        return NULL;

    // Execute a datatype-specific version of the algorithm. We generate
    // separate versions of the algorithm using C macros so we do not have to
    // continually switch on the datatype inside the implementation, saving CPU
    // cycles and decluttering the implementation.

    Py_BEGIN_ALLOW_THREADS
        switch (PyArray_TYPE(pBufferedImage))
        {
            case NPY_INT8:
                CAYULA_CORNILLON_FRONTS(pBufferedImage, pBufferedMask, pBufferedCandidateCounts, pBufferedFrontCounts, pBufferedWindowStatusCodes, pBufferedWindowStatusValues, bufferSize, histogramWindowSize, histogramWindowStride, minPropNonMaskedCells, minPopProp, minPopMeanDifference, minTheta, minSinglePopCohesion, minGlobalPopCohesion, npy_int8, -128, 127);
                break;

            case NPY_UINT8:
                CAYULA_CORNILLON_FRONTS(pBufferedImage, pBufferedMask, pBufferedCandidateCounts, pBufferedFrontCounts, pBufferedWindowStatusCodes, pBufferedWindowStatusValues, bufferSize, histogramWindowSize, histogramWindowStride, minPropNonMaskedCells, minPopProp, minPopMeanDifference, minTheta, minSinglePopCohesion, minGlobalPopCohesion, npy_uint8, 0, 255);
                break;

            case NPY_INT16:
                CAYULA_CORNILLON_FRONTS(pBufferedImage, pBufferedMask, pBufferedCandidateCounts, pBufferedFrontCounts, pBufferedWindowStatusCodes, pBufferedWindowStatusValues, bufferSize, histogramWindowSize, histogramWindowStride, minPropNonMaskedCells, minPopProp, minPopMeanDifference, minTheta, minSinglePopCohesion, minGlobalPopCohesion, npy_int16, -32768, 32767);
                break;

            case NPY_UINT16:
                CAYULA_CORNILLON_FRONTS(pBufferedImage, pBufferedMask, pBufferedCandidateCounts, pBufferedFrontCounts, pBufferedWindowStatusCodes, pBufferedWindowStatusValues, bufferSize, histogramWindowSize, histogramWindowStride, minPropNonMaskedCells, minPopProp, minPopMeanDifference, minTheta, minSinglePopCohesion, minGlobalPopCohesion, npy_uint16, 0, 65535);
                break;
        }
    Py_END_ALLOW_THREADS

    // Return successfully.

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef FrontsUtilsMethods[] =
{
    {"MedianFilter", MedianFilter, METH_VARARGS, "Executes a median filter on a buffered image. Only intended to be invoked from within GeoEco."},
    {"FocalSumOfMask", FocalSumOfMask, METH_VARARGS, "Executes a focal sum filter on a boolean mask. Only intended to be invoked from within GeoEco."},
    {"CayulaCornillonFronts", CayulaCornillonFronts, METH_VARARGS, "Cayula Cornillon (1992) single-image edge detection algorithm. Only intended to be invoked from within GeoEco."},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef FrontsUtilsmodule = {
    PyModuleDef_HEAD_INIT,
    "FrontUtils",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    FrontsUtilsMethods
};

PyMODINIT_FUNC
PyInit_FrontsUtils(void)
{
    import_array();
    return PyModule_Create(&FrontsUtilsmodule);
}
// Python2 implementation (obsolete)

//PyMODINIT_FUNC initFrontsUtils(void)
//{
//    // Initialize as a Python extension module.
//
//    Py_InitModule("FrontsUtils", FrontsUtilsMethods);
//
//    // Initialize numpy.
//
//    import_array();
//};
