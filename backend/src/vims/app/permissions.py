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

from vims.util import EnumStrLower


class Permission(EnumStrLower):
    ADMIN = EnumStrLower.auto()
    READ_USERS = EnumStrLower.auto()
    CREATE_USER = EnumStrLower.auto()
    READ_USER = EnumStrLower.auto()
    UPDATE_USER = EnumStrLower.auto()
    UPDATE_USER_PASSWORD = EnumStrLower.auto()
    DELETE_USER = EnumStrLower.auto()
    READ_ROLES = EnumStrLower.auto()
    CREATE_GROUP = EnumStrLower.auto()
    READ_GROUPS = EnumStrLower.auto()
    UPDATE_GROUP = EnumStrLower.auto()
    DELETE_GROUP = EnumStrLower.auto()
    READ_DATASETS_ALL = EnumStrLower.auto()
    READ_DATASETS_SHARED = EnumStrLower.auto()
    CREATE_DATASET = EnumStrLower.auto()
    READ_DATASET_ALL = EnumStrLower.auto()
    READ_DATASET_SHARED = EnumStrLower.auto()
    UPDATE_DATASET = EnumStrLower.auto()
    DELETE_DATASET = EnumStrLower.auto()
    READ_DATASOURCES = EnumStrLower.auto()
    CREATE_DATASOURCE = EnumStrLower.auto()
    READ_DATASOURCE = EnumStrLower.auto()
    UPDATE_DATASOURCE = EnumStrLower.auto()
    DELETE_DATASOURCE = EnumStrLower.auto()
    GET_DATASOURCE_DATASETS = EnumStrLower.auto()
    GET_DATASOURCE_DATASET_FIELDS = EnumStrLower.auto()
    READ_VISUALIZATIONS = EnumStrLower.auto()
    CREATE_VISUALIZATION = EnumStrLower.auto()
    READ_VISUALIZATION = EnumStrLower.auto()
    UPDATE_VISUALIZATION = EnumStrLower.auto()
    DELETE_VISUALIZATION = EnumStrLower.auto()
    READ_DASHBOARD = EnumStrLower.auto()
    READ_DASHBOARDS = EnumStrLower.auto()
    UPDATE_DASHBOARD = EnumStrLower.auto()
    CREATE_DASHBOARD = EnumStrLower.auto()
    DELETE_DASHBOARD = EnumStrLower.auto()
    READ_MAPS = EnumStrLower.auto()
    CREATE_MAP = EnumStrLower.auto()
    UPDATE_MAP = EnumStrLower.auto()
    DELETE_MAP = EnumStrLower.auto()
    UPLOAD_DATA = EnumStrLower.auto()
