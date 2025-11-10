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

from typing import Any, Dict

from datetime import datetime
from uuid import uuid4

from pydantic import EmailStr, Field

from .base import BaseModel


class DatasourceBase(BaseModel):
    display_name: str
    point_of_contact_email: EmailStr
    datasource_type: str


class DatasourceCreate(DatasourceBase):
    url: str
    password: str
    username: str | None = None
    ssl: bool | None = None
    min_connection_size: int | None = None
    max_connection_size: int | None = None


class DatasourceUpdate(DatasourceBase):
    url: str
    password: str
    username: str | None = None
    ssl: bool | None = None
    min_connection_size: int | None = None
    max_connection_size: int | None = None


class DatasourceInternal(DatasourceBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    token: str
    last_modified: datetime | None = None
    last_modified_by_user: str


class Datasource(DatasourceInternal):
    created: datetime = Field(default_factory=datetime.utcnow)
    created_by_user: str


class DatasourceConnectionInfo(Datasource):
    url: str
    password: str
    username: str | None = None
    ssl: bool | None = None
    min_connection_size: int | None = None
    max_connection_size: int | None = None


class DatasourceRecordUpsert(BaseModel):
    primary_key_field: str
    record: Dict[str, Any]


class DatasourceRecordDelete(BaseModel):
    primary_key_field: str
    primary_key_value: Any
