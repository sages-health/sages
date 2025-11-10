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

from vims.app.permissions import Permission
from vims.app.roles import Role

roles = {
    Role.ADMIN: [
        Permission.ADMIN,
    ],
    Role.DEVELOPER: [
        Permission.READ_USERS,
        Permission.CREATE_USER,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.UPDATE_USER_PASSWORD,
        Permission.DELETE_USER,
        Permission.READ_ROLES,
        Permission.CREATE_GROUP,
        Permission.READ_GROUPS,
        Permission.UPDATE_GROUP,
        Permission.DELETE_GROUP,
        Permission.READ_DATASETS_ALL,
        Permission.CREATE_DATASET,
        Permission.READ_DATASET_ALL,
        Permission.UPDATE_DATASET,
        Permission.DELETE_DATASET,
        Permission.READ_DATASOURCES,
        Permission.CREATE_DATASOURCE,
        Permission.READ_DATASOURCE,
        Permission.UPDATE_DATASOURCE,
        Permission.DELETE_DATASOURCE,
        Permission.READ_VISUALIZATIONS,
        Permission.CREATE_VISUALIZATION,
        Permission.READ_VISUALIZATION,
        Permission.UPDATE_VISUALIZATION,
        Permission.DELETE_VISUALIZATION,
        Permission.READ_MAPS,
        Permission.CREATE_MAP,
        Permission.UPDATE_MAP,
        Permission.DELETE_MAP,
    ],
    Role.USER: [
        Permission.READ_DATASET_SHARED,
        Permission.READ_DATASETS_SHARED,
        Permission.READ_VISUALIZATIONS,
        Permission.CREATE_VISUALIZATION,
        Permission.READ_VISUALIZATION,
        Permission.UPDATE_VISUALIZATION,
        Permission.DELETE_VISUALIZATION,
        Permission.READ_DATASOURCES,
        Permission.READ_DATASOURCE,
        Permission.CREATE_DASHBOARD,
        Permission.UPDATE_DASHBOARD,
        Permission.DELETE_DASHBOARD,
        Permission.READ_DASHBOARD,
        Permission.READ_DASHBOARDS,
        Permission.READ_MAPS,
    ],
    Role.VISUALIZATION_CREATOR: [
        Permission.READ_DATASETS_ALL,
        Permission.READ_DATASET_ALL,
        Permission.READ_DATASET_SHARED,
        Permission.READ_DATASETS_SHARED,
        Permission.READ_VISUALIZATIONS,
        Permission.CREATE_VISUALIZATION,
        Permission.READ_VISUALIZATION,
        Permission.UPDATE_VISUALIZATION,
        Permission.DELETE_VISUALIZATION,
    ],
}
