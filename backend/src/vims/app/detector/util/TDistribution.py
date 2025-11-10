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

import math

import numpy


# These functions are necessary to get normal and t distributions and their inverses
# Inverse normal: probability (0,1) gets converted to mean 0 variance 1 Gaussian value
def invnorm(p):
    t = (1 - p) if (p > 0.5) else p
    s = math.sqrt(-2.0 * math.log(t))
    a = 2.515517 + (0.802853 * s) + (0.010328 * s * s)
    b = 1 + (1.432788 * s) + (0.189269 * s * s) + (0.001308 * s * s * s)
    u = s - (a / b)
    return (-u) if (p < 0.5) else u


# Helper functions for t distribution (Log Gamma)
def LogGamma(Z):
    S = (
        1
        + 76.18009173 / Z
        - 86.50532033 / (Z + 1)
        + 24.01409822 / (Z + 2)
        - 1.231739516 / (Z + 3)
        + 0.00120858003 / (Z + 4)
        - 0.00000536382 / (Z + 5)
    )
    LG = (Z - 0.5) * math.log(Z + 4.5) - (Z + 4.5) + math.log(S * 2.50662827465)
    return LG


# Helper functions for t distribution - Beta(A,B)
def Betinc(X, A, B):
    A0 = 0
    B0 = 1
    A1 = 1
    B1 = 1
    M9 = 0
    A2 = 0

    while abs((A1 - A2) / A1) > 0.00001:
        A2 = A1
        C9 = -(A + M9) * (A + B + M9) * X / (A + 2 * M9) / (A + 2 * M9 + 1)
        A0 = A1 + C9 * A0
        B0 = B1 + C9 * B0
        M9 = M9 + 1
        C9 = M9 * (B - M9) * X / (A + 2 * M9 - 1) / (A + 2 * M9)
        A1 = A0 + C9 * A1
        B1 = B0 + C9 * B1
        A0 = A0 / B1
        B0 = B0 / B1
        A1 = A1 / B1
        B1 = 1
    return A1 / A


# The actual TDistribution object
# First cumulative probability
def cumulativeProbability(X, df):
    if df <= 0:
        print("Degrees of freedom must be positive")
    else:
        A = df / 2
        S = A + 0.5
        Z = df / (df + X * X)
        BT = numpy.exp(
            LogGamma(S)
            - LogGamma(0.5)
            - LogGamma(A)
            + A * math.log(Z)
            + 0.5 * (math.log(1 - Z) if 1 - Z != 0 else -math.inf)
        )

        if Z < (A + 1) / (S + 2):
            betacdf = BT * Betinc(Z, A, 0.5)
        else:
            betacdf = 1 - BT * Betinc(1 - Z, 0.5, A)
        if X < 0:
            tcdf = betacdf / 2
        else:
            tcdf = 1 - betacdf / 2

    return tcdf


# And inverse Cumulative Probability - the most difficult to get
# Uses a simple interpolation algorithm involving the straight t-distribution
# With normal values as starting guesses
# At 1e-10 precision, the value is correct up to about the 5th decimal
def inverseCumulativeProbability(T, df):
    epsilon = float(1e-10)
    diff = 1
    out = 0
    temp = 0
    if T > 0.5:
        out = invnorm(T)
    else:
        out = -invnorm(T)
    temp = cumulativeProbability(out, df)
    diff = numpy.sign(out) * (T - temp)
    diff2 = diff
    k = 0.5

    while abs(diff) > epsilon:
        if diff < 0:
            out2 = out * k
        else:
            out2 = (1 + k) * out
        temp = cumulativeProbability(out2, df)
        diff2 = numpy.sign(out2) * (T - temp)

        if numpy.sign(diff2) != numpy.sign(diff):
            k = k / 2
            if abs(diff2) < epsilon:
                out = out2
            out2 = out

        diff = diff2
        out = out2

    return out2
