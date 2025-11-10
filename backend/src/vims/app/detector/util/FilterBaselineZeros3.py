#  Copyright (c) 2013-2025. The Johns Hopkins University Applied Physics Laboratory LLC
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# NO WARRANTY.   THIS MATERIAL IS PROVIDED "AS IS."  JHU/APL DISCLAIMS ALL
# WARRANTIES IN THE MATERIAL, WHETHER EXPRESS OR IMPLIED, INCLUDING (BUT NOT
# LIMITED TO) ANY AND ALL IMPLIED WARRANTIES OF PERFORMANCE,
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF
# INTELLECTUAL PROPERTY RIGHTS. ANY USER OF THE MATERIAL ASSUMES THE ENTIRE
# RISK AND LIABILITY FOR USING THE MATERIAL.  IN NO EVENT SHALL JHU/APL BE
# LIABLE TO ANY USER OF THE MATERIAL FOR ANY ACTUAL, INDIRECT,
# CONSEQUENTIAL, SPECIAL OR OTHER DAMAGES ARISING FROM THE USE OF, OR
# INABILITY TO USE, THE MATERIAL, INCLUDING, BUT NOT LIMITED TO, ANY DAMAGES
# FOR LOST PROFITS.

import statistics


def filterBaselineZerosTest(d):
    medianVal = statistics.median(d)
    try:
        nonzeromedian = statistics.median(
            [d[i] for i in [j for j, v in enumerate(d) if v > 0.0]]
        )
    except statistics.StatisticsError:  # empty array
        nonzeromedian = 0
    return medianVal > 0 or nonzeromedian > 4


def filterBaselineZeros(data):

    dt = data[:]

    testData = []
    ndxOK = []
    ndxStart = []
    ndxEnd = []
    numZerosTest = []
    minNumZeros = 3
    dtOut = []
    thresholdProb = 0.01

    testData = dt[:]
    testData.insert(0, 1)

    for i in range(len(testData) - 1):
        if testData[i] != 0 and testData[i + 1] == 0:
            ndxStart.append(i)

    testData = dt[:]
    testData.append(1)

    for i in range(len(testData) - 1):
        if testData[i] == 0 and testData[i + 1] != 0:
            ndxEnd.append(i)

    w = 0

    for i in range(len(ndxStart)):
        numZerosTest.append([(ndxEnd[i] - ndxStart[i] + 1), i])

    numZerosTest.sort(reverse=True)

    for i in range(len(dt)):
        ndxOK.append(i)

    ndxtemp = ndxOK[:]

    for i in range(len(numZerosTest)):
        ndxtemp = ndxOK[:]
        key = numZerosTest[i][1]
        val = numZerosTest[i][0]
        k = 0

        if val < minNumZeros:
            continue

        if i == 0:
            k = ndxStart[key]

        elif ndxStart[key] > k:
            for w in range(len(ndxtemp) + 1):
                if ndxtemp[w] == ndxStart[key]:
                    break
            k = w
        else:
            for w in range(len(ndxtemp) + 1):
                if ndxtemp[w] == ndxStart[key]:
                    break
            k = w

        for j in range(ndxStart[key], ndxEnd[key] + 1, 1):
            del ndxtemp[k]

        NumValuesOut = len(ndxOK) - ndxEnd[key] + ndxStart[key] - 1

        if NumValuesOut == 0:
            break
        dtOut = [dt[i] for i in ndxtemp]
        nsum = 0
        for p in range(len(dtOut)):
            if dtOut[p] == 0:
                nsum += 1
        numZerosOut = max(1, nsum)

        if (numZerosOut / NumValuesOut) ** val > thresholdProb:
            break

        ndxOK = ndxtemp[:]

    dtOut = [dt[i] for i in ndxOK]
    nsum = 0
    for h in range(len(dtOut)):
        if dtOut[h] > 0:
            nsum += 1
    if nsum < 2:
        ndxOK = [0]

    return ndxOK
