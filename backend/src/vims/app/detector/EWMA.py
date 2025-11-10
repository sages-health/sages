#  Copyright (c) 2013-2025. The Johns Hopkins University Applied Physics Laboratory LLC
#
#
# This material may be used, modified, or reproduced by or for the U.S.
# Government pursuant to the rights granted under the clauses at
# DFARS 252.227-7013/7014 or FAR 52.227-14.
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

import math
import statistics

import numpy

from .util import FilterBaselineZeros3, TDistribution


def calculateEWMA(
    data,
    OMEGA=0.4,
    MIN_DEG_FREEDOM=2,
    MAX_BASELINE_LEN=28,
    THRESHOLD_PROBABILITY_RED_ALERT=0.01,
    THRESHOLD_PROBABILITY_YELLOW_ALERT=0.05,
    NUM_GUARDBAND=2,
    REMOVE_ZEROES=True,
    MIN_PROB_LEVEL=1e-6,
    NUM_FIT_PARAMS=1,
):

    # OMEGA the EWMA smoothing coefficient (between 0 and 1) default 0.4
    # MIN_DEG_FREEDOM the minimum number of degrees of freedom
    # MAX_BASELINE_LEN the maximum length of the baseline period

    # The one-sided threshold p-value for rejecting the null hypothesis,
    # corresponding to red alerts

    # THRESHOLD_PROBABILITY_RED_ALERT

    # The one-sided threshold p-value for rejecting the null hypothesis,
    # corresponding to yellow alerts

    # THRESHOLD_PROBABILITY_YELLOW_ALERT

    # the length of the guard band period

    # NUM_GUARDBAND = guardband

    # if true unusually long strings of zeros in the baseline period
    # are removed prior to applying process control

    # REMOVE_ZEROES = remove

    # MIN_PROB_LEVEL
    # NUM_FIT_PARAMS

    minBaseline = NUM_FIT_PARAMS + MIN_DEG_FREEDOM
    degFreedomRange = MAX_BASELINE_LEN - NUM_FIT_PARAMS

    cleanedData = list(map(lambda x: 0 if x is None else x, data))

    UCL_R = []
    UCL_Y = []
    sigmaCoeff = []
    deltaSigma = []
    minSigma = []
    degFreedom = [None] * len(cleanedData)
    term1 = OMEGA / (2.0 - OMEGA)
    term2 = []
    term3 = []

    for i in range(degFreedomRange):
        UCL_R.append(
            TDistribution.inverseCumulativeProbability(
                1 - THRESHOLD_PROBABILITY_RED_ALERT, i + 1
            )
        )
        UCL_Y.append(
            TDistribution.inverseCumulativeProbability(
                1 - THRESHOLD_PROBABILITY_YELLOW_ALERT, i + 1
            )
        )
        numBaseline = NUM_FIT_PARAMS + i + 1
        term2.append(1.0 / numBaseline)
        term3.append(
            -2.0
            * ((1 - OMEGA) ** (NUM_GUARDBAND + 1.0))
            * (1.0 - ((1 - OMEGA) ** numBaseline))
            / numBaseline
        )

        sigmaCoeff.append(math.sqrt(term1 + term2[i] + term3[i]))
        deltaSigma.append(
            (OMEGA / UCL_Y[i])
            * (
                0.1289
                - (0.2414 - 0.1826 * ((1 - OMEGA) ** 4))
                * math.log(10.0 * THRESHOLD_PROBABILITY_YELLOW_ALERT)
            )
        )

        minSigma.append((OMEGA / UCL_Y[i]) * (1.0 + 0.5 * ((1 - OMEGA) ** 2)))

    pvalues = [None] * len(cleanedData)
    test_stat = [None] * len(cleanedData)
    sigma = []
    testBase = []
    baselineData = []
    expectedDataArray = [None] * len(cleanedData)

    # initialize the smoothed data
    smoothedData = cleanedData[0]
    for m in range(1, min(minBaseline + NUM_GUARDBAND, len(cleanedData)), 1):
        smoothedData = OMEGA * cleanedData[m] + (1 - OMEGA) * smoothedData

    # initialize the indices of the baseline period
    ndxBaseline = []
    for i in range(minBaseline - 1):
        ndxBaseline.append(i)

    # loop through the days on which to make predictions
    for j in range(minBaseline + NUM_GUARDBAND, len(cleanedData), 1):
        # smooth the data using an exponentially weighted moving average (EWMA)
        smoothedData = OMEGA * cleanedData[j] + (1 - OMEGA) * smoothedData

        # lengthen and advance the baseline period
        if len(ndxBaseline) < 1 or (
            ndxBaseline[len(ndxBaseline) - 1] + 1 < MAX_BASELINE_LEN
        ):
            ndxBaseline.insert(0, -1)

        # advance the indices of the baseline period
        ndxBaseline = [x + 1 for x in ndxBaseline]

        testBase = [cleanedData[i] for i in ndxBaseline]
        baselineData = [cleanedData[i] for i in ndxBaseline]

        if REMOVE_ZEROES and FilterBaselineZeros3.filterBaselineZerosTest(testBase):
            ndxOK = FilterBaselineZeros3.filterBaselineZeros(testBase)
            baselineData = [testBase[i] for i in ndxOK]

        else:
            baselineData = testBase[:]

        # check the baseline period is filled with zeros; no prediction can be
        if all(x == 0 for x in baselineData):
            continue

        # the number of degrees of freedom
        degFreedom[j] = len(baselineData) - NUM_FIT_PARAMS
        if degFreedom[j] < MIN_DEG_FREEDOM:
            continue

        # the predicted current value of the data
        expectedData = statistics.mean(baselineData)
        expectedDataArray[j] = expectedData

        # calculate the test statistic
        # the adjusted standard deviation of the baseline data
        sigma = (
            sigmaCoeff[degFreedom[j] - 1] * statistics.stdev(baselineData)
            + deltaSigma[degFreedom[j] - 1]
        )
        # don't allow values smaller than MinSigma
        sigma = max(sigma, minSigma[degFreedom[j] - 1])
        # the test statistic

        test_stat[j] = (smoothedData - expectedData) / sigma
        if abs(test_stat[j]) > UCL_R[degFreedom[j] - 1]:
            smoothedData = (
                expectedData
                + numpy.sign(test_stat[j]) * UCL_R[degFreedom[j] - 1] * sigma
            )

    for k in range(len(cleanedData)):
        if test_stat[k] is None:
            continue
        elif abs(test_stat[k]) > 0.0:
            pvalues[k] = 1 - TDistribution.cumulativeProbability(
                test_stat[k], degFreedom[k]
            )
            if pvalues[k] < MIN_PROB_LEVEL:
                pvalues[k] = MIN_PROB_LEVEL

    return [pvalues, expectedDataArray]
