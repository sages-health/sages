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

from enum import Enum


class DataBridgeType(Enum):
    SQL_ALCHEMY = "sql_alchemy"
    VIMS = "vims"


class DataBridge:
    def __init__(self, token="", display_name="", datasource_type=""):
        self.token = token
        self.display_name = display_name
        self.datasource_type = datasource_type

    def get_datasource_type(self):
        return self.datasource_type

    def get_token(self):
        return self.token

    def get_display_name(self):
        return self.display_name

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def query(self, query_args: Dict[str, Any]):
        raise NotImplementedError

    def record_exists(self, table_name, fields, primary_key_field, primary_key_value):
        raise NotImplementedError

    def create_record(self, table_name, fields, record):
        raise NotImplementedError

    def update_record(
        self, table_name, fields, record, primary_key_field, primary_key_value
    ):
        raise NotImplementedError

    def delete_record(self, table_name, fields, primary_key_field, primary_key_value):
        raise NotImplementedError

    def ping(self):
        raise NotImplementedError

    def list_datasets(self) -> List[Dict[str, str]]:
        # Returns a list of datasets and their display names.
        raise NotImplementedError

    def get_dataset_fields(self, dataset_name: str):
        # Returns a list of dataset fields and their python type.
        raise NotImplementedError

    def get_dataset_field_values(self, dataset_name: str, field_name: str):
        raise NotImplementedError
