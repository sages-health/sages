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

from typing import Dict

from fastapi import APIRouter, Depends

from ..auth import Permission, require_permission
from .CusumSagesDetector import calculateCUSUM
from .Ears import calculateC1, calculateC2, calculateC3, calculateEARS
from .EWMA import calculateEWMA


def detector():
    router = APIRouter()

    @router.post(
        "/cusum",
        dependencies=[Depends(require_permission(Permission.READ_DATASET_SHARED))],
    )
    async def post_cusum(params: Dict):
        # Initialize Parameters
        #  cusum_k = 0.5
        #  baseline = 28
        #  guardband = 2
        #  min_sigma = 0.5
        #  reset_level = 4

        data = None
        cusum_k = 0.5
        baseline = 28
        guardband = 2
        min_sigma = 0.5
        reset_level = 4

        if "data" in params:
            data = params["data"]

        if "cusum_k" in params:
            cusum_k = params["cusum_k"]

        if "baseline" in params:
            baseline = params["baseline"]

        if "guardband" in params:
            guardband = params["guardband"]

        if "min_sigma" in params:
            min_sigma = params["min_sigma"]

        if "reset_level" in params:
            reset_level = params["reset_level"]

        [pvalues, expectedData] = calculateCUSUM(
            data, cusum_k, baseline, guardband, min_sigma, reset_level
        )

        params = {
            "data": data,
            "cusum_k": cusum_k,
            "baseline": baseline,
            "guardband": guardband,
            "min_sigma": min_sigma,
            "reset_level": reset_level,
        }

        return {"params": params, "pValues": pvalues, "expectedData": expectedData}

    @router.post(
        "/ears",
        dependencies=[Depends(require_permission(Permission.READ_DATASET_SHARED))],
    )
    async def post_ears(params: Dict):
        data = None
        baseline = None
        base_lag = None
        cusum_flag = None
        cusum_k = None
        min_sigma = None
        thresh = None

        if "data" in params:
            data = params["data"]

        if "baseline" in params:
            baseline = params["baseline"]

        if "base_lag" in params:
            base_lag = params["base_lag"]

        if "cusum_flag" in params:
            cusum_flag = params["cusum_flag"]

        if "cusum_k" in params:
            cusum_k = params["cusum_k"]

        if "min_sigma" in params:
            min_sigma = params["min_sigma"]

        if "thresh" in params:
            thresh = params["thresh"]

        [earStat, expectedData] = calculateEARS(
            data, baseline, base_lag, cusum_flag, cusum_k, min_sigma, thresh
        )

        params = {
            "data": data,
            "baseline": baseline,
            "base_lag": base_lag,
            "cusum_flag": cusum_flag,
            "cusum_k": cusum_k,
            "min_sigma": min_sigma,
            "thresh": thresh,
        }

        return {"params": params, "earStat": earStat, "expectedData": expectedData}

    @router.post(
        "/cdc1",
        dependencies=[Depends(require_permission(Permission.READ_DATASET_SHARED))],
    )
    async def post_cdc1(params: Dict):
        data = None

        if "data" in params:
            data = params["data"]

        [earStat, expectedData] = calculateC1(data)

        params = {"data": data}

        return {"params": params, "earStat": earStat, "expectedData": expectedData}

    @router.post(
        "/cdc2",
        dependencies=[Depends(require_permission(Permission.READ_DATASET_SHARED))],
    )
    async def post_cdc2(params: Dict):
        data = None

        if "data" in params:
            data = params["data"]

        [earStat, expectedData] = calculateC2(data)

        params = {"data": data}

        return {"params": params, "earStat": earStat, "expectedData": expectedData}

    @router.post(
        "/cdc3",
        dependencies=[Depends(require_permission(Permission.READ_DATASET_SHARED))],
    )
    async def post_cdc3(params: Dict):
        data = None

        if "data" in params:
            data = params["data"]

        [earStat, expectedData] = calculateC3(data)

        params = {"data": data}

        return {"params": params, "earStat": earStat, "expectedData": expectedData}

    @router.post(
        "/ewma",
        dependencies=[Depends(require_permission(Permission.READ_DATASET_SHARED))],
    )
    async def post_ewma(params: Dict):
        # Initialize Parameters
        #  omega = 0.4
        #  min_deg_freedom = 2
        #  max_base_line_len = 28
        #  threshold_probability_red_alert = 0.01
        #  threshold_probability_yellow_alert = 0.05
        #  num_guardband = 2
        #  remove_zeros = True
        #  min_prob_level = 1E-6
        #  num_fit_params = 1

        data = None
        omega = 0.4
        min_deg_freedom = 2
        max_base_line_len = 28
        threshold_probability_red_alert = 0.01
        threshold_probability_yellow_alert = 0.05
        num_guardband = 2
        remove_zeros = True
        min_prob_level = 1e-6
        num_fit_params = 1

        if "data" in params:
            data = params["data"]

        if "omega" in params:
            omega = params["omega"]

        if "min_deg_freedom" in params:
            min_deg_freedom = params["min_deg_freedom"]

        if "max_base_line_len" in params:
            max_base_line_len = params["max_base_line_len"]

        if "threshold_probability_red_alert" in params:
            threshold_probability_red_alert = params["threshold_probability_red_alert"]

        if "threshold_probability_yellow_alert" in params:
            threshold_probability_yellow_alert = params[
                "threshold_probability_yellow_alert"
            ]

        if "num_guardband" in params:
            num_guardband = params["num_guardband"]

        if "remove_zeros" in params:
            remove_zeros = params["remove_zeros"]

        if "min_prob_level" in params:
            min_prob_level = params["min_prob_level"]

        if "num_fit_params" in params:
            num_fit_params = params["num_fit_params"]

        [pvalues, expectedData] = calculateEWMA(
            data,
            omega,
            min_deg_freedom,
            max_base_line_len,
            threshold_probability_red_alert,
            threshold_probability_yellow_alert,
            num_guardband,
            remove_zeros,
            min_prob_level,
            num_fit_params,
        )

        params = {
            "data": data,
            "omega": omega,
            "min_deg_freedom": min_deg_freedom,
            "max_base_line_len": max_base_line_len,
            "threshold_probability_red_alert": threshold_probability_red_alert,
            "threshold_probability_yellow_alert": threshold_probability_yellow_alert,
            "num_guardband": num_guardband,
            "remove_zeros": remove_zeros,
            "min_prob_level": min_prob_level,
            "num_fit_params": num_fit_params,
        }

        return {"params": params, "pValues": pvalues, "expectedData": expectedData}

    return router
