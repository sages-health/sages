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

from typing import Any, Dict, List

from datetime import datetime
from uuid import uuid4

from pydantic import Field

from .base import BaseModel

# class TypeEnum(Enum):
#     table = "table"
#     scatter = "scatter"
#     bar = "bar"


class VisualizationConfig(BaseModel):
    visualization_type: str
    visualization_options: Dict[str, Any] | None = None
    dataset_id: str
    dataset_filtered_shared_fields: List[str] | None = None
    dataset_field_requests: Dict[str, Any] | None = None
    date_field: str | None = None


class VisualizationBase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    visualization_name: str
    overlay: bool
    configs: List[VisualizationConfig]


class VisualizationInternal(VisualizationBase):
    last_modified: datetime | None = None
    last_modified_by_user: str


class Visualization(VisualizationInternal):
    created: datetime = Field(default_factory=datetime.utcnow)
    created_by_user: str
