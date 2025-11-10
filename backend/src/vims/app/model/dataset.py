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

from typing import Any, Dict, List, Union

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import Field

from vims.util import EnumStrLower

from .base import BaseModel


class DateGranularityEnum(EnumStrLower):
    DAILY = EnumStrLower.auto()
    WEEKLY = EnumStrLower.auto()
    MONTHLY = EnumStrLower.auto()
    YEARLY = EnumStrLower.auto()
    EPIWEEK = EnumStrLower.auto()


class DatasetField(BaseModel):
    display_name: str
    data_field_name: str
    data_field_type: str
    date_granularity: DateGranularityEnum | None = None
    is_reference: bool
    values: List[Union[str, None]] | None = None
    region_map_id: str | None = None
    region_map_mapping: Dict[str, str] | None = None

    class Config:
        use_enum_values = True


class DataList(BaseModel):
    value: List[float]


class OrderEnum(Enum):
    ascending = "asc"
    descending = "desc"


class DatasetQuery(BaseModel):
    computed: Dict[str, Dict[str, Union[str, List[str]]]] | None = None
    request: Dict[str, Any] | None = None
    projection: Dict[str, bool] | None = None
    group_by: Dict[str, Any] | None = None
    limit: int | None = None
    offset: int = 0
    order_by: List[List[Union[str, OrderEnum]]] | None = None
    transformations: Dict[str, Any] | None = None
    count_fields: List[str] | None = None
    distinct_field: str | None = None

    class Config:
        use_enum_values = True


class DatasetBase(BaseModel):
    dataset_name: str
    dataset_display_name: str
    description: str | None = None
    display_name: str
    # is_aggregate: bool
    datasource_id: str
    fields: List[DatasetField] = Field(default_factory=list)
    is_active: bool
    expiration: datetime | None = None
    primary_key_field: str | None = None
    date_field: str | None = None
    shared_with: List[str] | None = None
    groups: List[str] | None = None


class DatasetInternal(DatasetBase):
    last_modified: datetime | None = None
    last_modified_by_user: str


class Dataset(DatasetInternal):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created: datetime = Field(default_factory=datetime.utcnow)
    created_by_user: str


class DatasetBaseQuery(DatasetBase):
    base_query: DatasetQuery | None = None


class DatasetAdminInternal(DatasetBaseQuery):
    id: str = Field(default_factory=lambda: str(uuid4()))
    last_modified: datetime | None = None
    last_modified_by_user: str


class DatasetAdmin(DatasetAdminInternal):
    created: datetime = Field(default_factory=datetime.utcnow)
    created_by_user: str


class DatasetRecord(DatasetBase):
    record: Dict[str, Any]


class DatasetRecordDelete(BaseModel):
    primary_key_field: str
    primary_key_value: Any
