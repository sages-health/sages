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

import uuid

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    PickleType,
    String,
    Table,
    func,
)
from sqlalchemy.ext.mutable import MutableList

metadata = MetaData()


def uuid_gen():
    return lambda: str(uuid.uuid4())


users = Table(
    "user",
    metadata,
    Column("id", String, primary_key=True, default=uuid_gen),
    Column("username", String, index=True),
    Column("email", String),
    Column("password", String),
    Column("password_last_updated", DateTime, default=func.now()),
    Column("password_history", MutableList.as_mutable(PickleType), default=list),
    Column("enabled", Boolean, default=True),
    Column("remote", Boolean, default=False),
    Column("last_modified", DateTime, onupdate=datetime.utcnow),
    Column("created", DateTime, default=func.now()),
    Column("first_name", String),
    Column("last_name", String),
    Column("organization", String),
    Column("permissions", JSON),
    Column("phone_number", String),
    Column("roles", JSON),
    Column("groups", MutableList.as_mutable(PickleType)),
)

user_login_tracking = Table(
    "userlogintracking",
    metadata,
    Column("user", String, primary_key=True, unique=True),
    Column("attempts", Integer),
    Column("last_attempt", DateTime),
    Column("locked_until", DateTime),
)

tokens = Table(
    "token",
    metadata,
    Column("id", String, primary_key=True, default=uuid_gen),
    Column("expires", DateTime),
    Column("user", String),
)

user_security_settings = Table(
    "usersecuritysettings",
    metadata,
    Column("user", String, primary_key=True, unique=True),
    Column("otp_enabled", Boolean, default=False),
    Column("secret", String),
)

maps = Table(
    "map",
    metadata,
    Column("id", String, primary_key=True, default=uuid_gen),
    Column("center", JSON),
    Column("created", DateTime, default=func.now()),
    Column("created_by_user", Integer),
    Column("last_modified", DateTime, onupdate=datetime.utcnow),
    Column("last_modified_by_user", Integer),
    Column("display_name", String),
    Column("regions", MutableList.as_mutable(PickleType)),
    Column("zoom", Integer),
)

groups = Table(
    "group",
    metadata,
    Column("id", String, primary_key=True, default=uuid_gen),
    Column("center", JSON),
    Column("created", DateTime, default=func.now()),
    Column("created_by_user", Integer),
    Column("last_modified", DateTime, onupdate=datetime.utcnow),
    Column("last_modified_by_user", Integer),
    Column("group_name", String),
)

datasources = Table(
    "datasource",
    metadata,
    Column("id", String, primary_key=True, default=uuid_gen),
    Column("center", JSON),
    Column("created", DateTime, default=func.now()),
    Column("created_by_user", Integer),
    Column("last_modified", DateTime, onupdate=datetime.utcnow),
    Column("last_modified_by_user", Integer),
    Column("display_name", String),
    Column("point_of_contact_email", String),
    Column("token", String),
    Column("datasource_type", String),
    Column("url", String),
    Column("password", String),
    Column("kwargs", JSON),
)

datasets = Table(
    "dataset",
    metadata,
    Column("id", String, primary_key=True, default=uuid_gen),
    Column("center", JSON),
    Column("created", DateTime, default=func.now()),
    Column("created_by_user", Integer),
    Column("last_modified", DateTime, onupdate=datetime.utcnow),
    Column("last_modified_by_user", Integer),
    Column("base_query", JSON),
    Column("dataset_name", String),
    Column("dataset_display_name", String),
    Column("datasource_id", String),
    Column("display_name", String),
    Column("primary_key_field", String),
    Column("date_field", String),
    Column("description", String),
    Column("expiration", String),
    Column("fields", MutableList.as_mutable(PickleType)),
    Column("groups", MutableList.as_mutable(PickleType)),
    Column("is_active", Boolean),
    Column("shared_with", String),
)

dashboards = Table(
    "dashboard",
    metadata,
    Column("id", String, primary_key=True, default=uuid_gen),
    Column("created", DateTime, default=func.now()),
    Column("created_by_user", Integer),
    Column("last_modified", DateTime, onupdate=datetime.utcnow),
    Column("last_modified_by_user", Integer),
    Column("archived", Boolean),
    Column("colNum", Integer),
    Column("description", String),
    Column("filters", String),
    Column("name", String),
    Column("visualizations", MutableList.as_mutable(PickleType)),
)


visualizations = Table(
    "visualization",
    metadata,
    Column("id", String, primary_key=True, default=uuid_gen),
    Column("created", DateTime, default=func.now()),
    Column("created_by_user", Integer),
    Column("last_modified", DateTime, onupdate=datetime.utcnow),
    Column("last_modified_by_user", Integer),
    Column("configs", MutableList.as_mutable(PickleType)),
    Column("colNum", Integer),
    Column("overlay", Boolean),
    Column("visualization_name", String),
)
