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

import pandas as pd

from vims.util import append_epiweek, sort_and_hash_dict

original_epiweek_data = [
    {"INICIO SINTOMAS": "03/06/2022", "SEMANA": "2022W22"},
    {"INICIO SINTOMAS": "11/07/2022", "SEMANA": "2022W28"},
    {"INICIO SINTOMAS": "08/05/2022", "SEMANA": "2022W19"},
    {"INICIO SINTOMAS": "27/06/2022", "SEMANA": "2022W26"},
    {"INICIO SINTOMAS": "27/06/2022", "SEMANA": "2022W26"},
    {"INICIO SINTOMAS": "04/05/2022", "SEMANA": "2022W18"},
    {"INICIO SINTOMAS": "20/05/2022", "SEMANA": "2022W20"},
    {"INICIO SINTOMAS": "17/04/2022", "SEMANA": "2022W16"},
    {"INICIO SINTOMAS": "16/08/2022", "SEMANA": "2022W33"},
]


def test_utils__generate_table_metadata_hash():
    table = {
        "gamma": "float",
        "beta": "int",
        "alpha": "datetime",
        "delta": "str",
    }

    table_sorted = {
        "alpha": "datetime",
        "beta": "int",
        "delta": "str",
        "gamma": "float",
    }

    assert sort_and_hash_dict(table) == sort_and_hash_dict(table_sorted)


def test_utils__append_epi_week():
    df = pd.DataFrame(original_epiweek_data)
    df["INICIO SINTOMAS"] = pd.to_datetime(df["INICIO SINTOMAS"], dayfirst=True)
    data_with_epiweek = append_epiweek(df, {"INICIO SINTOMAS": None})

    assert len(df) == len(data_with_epiweek)

    for original, calculated in zip(df.to_dict("records"), data_with_epiweek):
        assert original["SEMANA"] == calculated["epiweek_INICIO SINTOMAS"]
