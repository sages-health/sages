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

import datetime

import pytest

import vims.util.sqla_where_compiler as swc


@pytest.mark.parametrize(
    "to_parse,target",
    [
        (
            {
                swc.LogicalOps.AND.value: [
                    {"col1": {swc.ComparisonOps.EQ.value: 17}},
                    {"col2": {swc.ComparisonOps.IN.value: [1, 2, 3]}},
                ]
            },
            "(col1 == 17) and (col2 in [1, 2, 3])",
        ),
        (
            {
                swc.LogicalOps.OR.value: [
                    {"col1": {swc.ComparisonOps.EQ.value: 17}},
                    {"col2": {swc.ComparisonOps.IN.value: [1, 2, 3]}},
                ]
            },
            "(col1 == 17) or (col2 in [1, 2, 3])",
        ),
        (
            {
                swc.LogicalOps.NOT.value: {
                    swc.LogicalOps.NOT.value: {
                        "col1": {swc.ComparisonOps.EQ.value: 17}
                    },
                }
            },
            "not (not (col1 == 17))",
        ),
        (
            {
                swc.LogicalOps.AND.value: [
                    {
                        swc.LogicalOps.OR.value: [
                            {"col1": {swc.ComparisonOps.EQ.value: 17}},
                            {"col2": {swc.ComparisonOps.IN.value: [1, 2, 3]}},
                        ]
                    },
                    {"pet type": {swc.ComparisonOps.IN.value: ["dog", "cat"]}},
                ]
            },
            "((col1 == 17) or (col2 in [1, 2, 3])) and (pet type in ['dog', 'cat'])",
        ),
        (
            {
                swc.LogicalOps.NOT.value: {
                    swc.LogicalOps.AND.value: [
                        {
                            swc.LogicalOps.OR.value: [
                                {"col1": {swc.ComparisonOps.EQ.value: 17}},
                                {"col2": {swc.ComparisonOps.IN.value: [1, 2, 3]}},
                            ]
                        },
                        {"pet type": {swc.ComparisonOps.IN.value: ["d", "c"]}},
                    ]
                }
            },
            "not (((col1 == 17) or (col2 in [1, 2, 3])) and (pet type in ['d', 'c']))",
        ),
    ],
)
def test__parser__logical_expressions(to_parse: dict, target: str):
    parsed_expr = swc.SQLAWhereExpression.parse_children(to_parse, top_level=True)
    assert str(parsed_expr) == target


@pytest.mark.parametrize(
    "to_parse,target",
    [
        ({"col1": {swc.ComparisonOps.EQ.value: 17}}, "col1 == 17"),
        ({"test column": {swc.ComparisonOps.NE.value: 17}}, "test column != 17"),
        (
            {
                "testing date": {
                    swc.ComparisonOps.GT.value: datetime.datetime(2020, 12, 25)
                }
            },
            f"testing date > {str(datetime.datetime(2020, 12, 25))}",
        ),
        (
            {"temperature": {swc.ComparisonOps.GE.value: 17.12313}},
            "temperature >= 17.12313",
        ),
        (
            {"temperature": {swc.ComparisonOps.LE.value: 17.12313}},
            "temperature <= 17.12313",
        ),
        (
            {"temperature": {swc.ComparisonOps.LT.value: 17.12313}},
            "temperature < 17.12313",
        ),
        (
            {"pet type": {swc.ComparisonOps.IN.value: ["dog", "cat"]}},
            "pet type in ['dog', 'cat']",
        ),
        (
            {"pet type": {swc.ComparisonOps.NIN.value: ["dog", "cat"]}},
            "pet type not in ['dog', 'cat']",
        ),
        ({"state": {swc.ComparisonOps.LIKE.value: "aryland"}}, "state like aryland"),
        ({"state": {swc.ComparisonOps.ILIKE.value: "aryland"}}, "state ilike aryland"),
        (
            {"state": {swc.ComparisonOps.NOTLIKE.value: "aryland"}},
            "state not like aryland",
        ),
        (
            {"state": {swc.ComparisonOps.NOTILIKE.value: "aryland"}},
            "state not ilike aryland",
        ),
        (
            {"state": {swc.ComparisonOps.STARTSWITH.value: "aryland"}},
            "state starts with aryland",
        ),
        (
            {"state": {swc.ComparisonOps.ENDSWITH.value: "aryland"}},
            "state ends with aryland",
        ),
        (
            {"state": {swc.ComparisonOps.CONTAINS.value: "aryland"}},
            "state contains aryland",
        ),
        ({"state": {swc.ComparisonOps.IS.value: None}}, "state is None"),
    ],
)
def test__parser__column_expressions(to_parse: dict, target: str):
    parsed_expr = swc.SQLAWhereExpression.parse_children(to_parse, top_level=True)
    assert str(parsed_expr) == target


@pytest.mark.parametrize(
    "to_parse",
    [
        {},
        {"test"},
        [],
        ["test"],
        {"pet type": {swc.ComparisonOps.IN.value: 12}},
        {"pet type": {swc.ComparisonOps.NIN.value: 12}},
        {"pet type": {swc.ComparisonOps.LIKE.value: 12}},
        {"pet type": {swc.ComparisonOps.NOTLIKE.value: 12}},
        {
            swc.LogicalOps.NOT.value: [
                {"col1": {swc.ComparisonOps.EQ.value: 17}},
                {"col2": {swc.ComparisonOps.IN.value: [1, 2, 3]}},
            ]
        },
        {swc.LogicalOps.AND.value: []},
        {
            swc.LogicalOps.OR.value: {"col1": {swc.ComparisonOps.EQ.value: 17}},
        },
        {swc.LogicalOps.AND.value: {swc.ComparisonOps.EQ.value: 17}},
        {swc.ComparisonOps.EQ.value: 17},
        {"pet type": {"in": [1, 2, 3, 4]}},
    ],
)
def test__parser__malformatted(to_parse):
    with pytest.raises(swc.SqlaWhereParseError):
        swc.SQLAWhereExpression.parse_children(to_parse, top_level=True)
