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

from typing import Any, Dict, List, Optional, Set, Union

import enum
import hashlib
import importlib.util
import json
import sys

from collections import OrderedDict
from datetime import date, datetime
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd

from epiweeks import Week

from ..types import PathLike


class InvalidTypeCast(Exception):
    pass


class TransformationException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EnumStrLower(Enum):
    def _generate_next_value_(name, *_):
        return f"{name}".lower()

    @classmethod
    def auto(cls):
        return enum.auto()

    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)


class EpiweekFormat(EnumStrLower):
    iso = EnumStrLower.auto()
    cdc = EnumStrLower.auto()


class AggregateFunction(EnumStrLower):
    sum = EnumStrLower.auto()
    mean = EnumStrLower.auto()


class DatePart(EnumStrLower):
    month = EnumStrLower.auto()
    day = EnumStrLower.auto()
    year = EnumStrLower.auto()
    week = EnumStrLower.auto()


class AgeUnitEnum:
    # TODO: Set up i18n for age display backend
    DAYS = " Días"
    MONTHS = " Meses"
    YEARS = " Años"


date_part_lookup = {"month": datetime.month, "day": datetime.day, "year": datetime.year}


def find_upwards(file: PathLike, start: PathLike):
    root = Path(start)
    stop = Path(root.anchor)
    while True:
        path = root / file
        if path.exists():
            return path
        if root == stop:
            break
        root = root.parent
    return None


def load_dynamic(module: str, file: PathLike):
    file = str(Path(file).absolute())
    module_spec = importlib.util.spec_from_file_location(module, file)
    sys.modules[module] = module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def async_partial(func, *args, **kwargs):
    async def async_partial_inner(*iargs, **ikwargs):
        return await func(*args, *iargs, **kwargs, **ikwargs)

    return async_partial_inner


def sort_and_hash_dict(dict_in: Dict[Any, Any]):
    # Sort the given dict
    ordered_dict = OrderedDict(sorted(dict_in.items()))
    ordered_json = json.dumps(ordered_dict)
    return hashlib.sha1(ordered_json.encode("utf-8")).hexdigest()


def cast(input: str, _type: str):
    if input is None:
        return None
    if _type == "str":
        return input
    elif _type == "int":
        return int(input)
    elif _type == "float":
        return float(input)
    elif _type == "datetime":
        if isinstance(input, date):
            return datetime.fromisoformat(date.isoformat(input))
        else:
            return datetime.fromisoformat(input)
    else:
        raise InvalidTypeCast(f"{_type} is not one of (str|int|float|datetime).")


# https://stackoverflow.com/a/22238613.
def serialize_json(obj: Any):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


def deserialize_json(obj: Any):
    return obj


def week_to_iso(x: Week):
    return x.isoformat()


def week_to_cdc(x: Week):
    return x.cdcformat()


def append_epiweek(
    input_data: Union[List[Dict], pd.DataFrame],
    date_cols: Optional[Set[str]] = None,
    date_cols_renames: Optional[Dict[str, str]] = None,
    drop_existing: bool = False,
    epiweek_format: EpiweekFormat = EpiweekFormat.iso,
    aggregate_cols: Optional[List[str]] = None,
    count_col: Optional[str] = None,
    agg_func: AggregateFunction = None,
):
    df = pd.DataFrame(input_data)

    # if no date columns are specified, just convert all columns of datetime64 type
    if not date_cols:
        date_cols = set()
        for col_name in df.select_dtypes(include=[np.datetime64]):
            date_cols.add(col_name)

    if not date_cols_renames:
        date_cols_renames = {}

    for date_col in date_cols:
        if date_col not in df.columns:
            raise TransformationException(f"Column {date_col} not found in dataset.")
        new_col_name = date_cols_renames.get(date_col, f"epiweek_{date_col}")

        if epiweek_format == EpiweekFormat.iso:
            format_func = week_to_iso
        elif epiweek_format == EpiweekFormat.cdc:
            format_func = week_to_cdc
        else:
            raise TransformationException(
                f"Unsupported epiweek format '{epiweek_format}'"
            )

        df[new_col_name] = (
            df[date_col]
            .apply(pd.to_datetime)
            .apply(Week.fromdate)
            .apply(format_func)
            # TODO
            # .apply(
            #  lambda x: pd.to_datetime(f"{x.year}-{x.week:02d}-1", format="%G-%V-%u")
            # )
        )

    if aggregate_cols:
        df_type = {col: "string" for col in aggregate_cols}
        df_type[count_col] = "float"
        df = df.astype(df_type)
        if agg_func.lower() == AggregateFunction.sum.value:
            df = df.groupby(str(aggregate_cols)).sum(numeric_only=True).reset_index()
        elif agg_func.lower() == AggregateFunction.mean.value:
            df = df.groupby(str(aggregate_cols)).mean(numeric_only=True).reset_index()
        else:
            raise TransformationException(f"Invalid aggregation function {agg_func}")

    if drop_existing:
        for date_col in date_cols:
            df.rename(columns={f"epiweek_{date_col}": date_col}, inplace=True)

    # return a list of dicts not a DF
    return df.to_dict("records")


def append_date_part(
    input_data: Union[List[Dict], pd.DataFrame],
    date_cols: Optional[Set[str]] = None,
    date_cols_renames: Optional[Dict[str, str]] = None,
    drop_existing: bool = False,
    date_part: DatePart = DatePart.month,
    aggregate_cols: Optional[List[str]] = None,
    count_col: Optional[str] = None,
    agg_func: AggregateFunction = None,
):
    df = pd.DataFrame(input_data)

    # if no date columns are specified, just convert all columns of datetime64 type
    if not date_cols:
        date_cols = set()
        for col_name in df.select_dtypes(include=[np.datetime64]):
            date_cols.add(col_name)

    if not date_cols_renames:
        date_cols_renames = {}

    for date_col in date_cols:
        if date_col not in df.columns:
            raise TransformationException(f"Column {date_col} not found in dataset.")
        new_col_name = date_cols_renames.get(date_col, f"{date_part}_{date_col}")
        if date_part == DatePart.month.value:
            df[new_col_name] = (
                df[date_col]
                .apply(pd.to_datetime)
                .apply(lambda x: f"{x.year}-{x.month:02d}")
            )
        elif date_part == DatePart.day.value:
            df[new_col_name] = (
                df[date_col]
                .apply(pd.to_datetime)
                .apply(lambda x: f"{x.year}-{x.month:02d}-{x.day:02d}")
            )
        elif date_part == DatePart.year.value:
            df[new_col_name] = (
                df[date_col].apply(pd.to_datetime).apply(lambda x: x.year)
            )
        elif date_part == DatePart.week.value:
            df[new_col_name] = (
                df[date_col]
                .apply(pd.to_datetime)
                .apply(
                    lambda x: pd.to_datetime(
                        f"{x.year}-{x.week:02d}-1", format="%G-%V-%u"
                    ),
                )
            )
        else:
            raise

    if aggregate_cols:
        df_type = {col: "string" for col in aggregate_cols}
        df_type[count_col] = "float"
        df = df.astype(df_type)
        if agg_func.lower() == AggregateFunction.sum.value:
            df = df.groupby(aggregate_cols).sum(numeric_only=True).reset_index()
        elif agg_func.lower() == AggregateFunction.mean.value:
            df = df.groupby(aggregate_cols).mean(numeric_only=True).reset_index()
        else:
            raise TransformationException(f"Invalid aggregation function {agg_func}")

    if drop_existing:
        for date_col in date_cols:
            df.rename(columns={f"{date_part}_{date_col}": date_col}, inplace=True)

    # return a list of dicts not a DF
    return df.to_dict("records")
