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

import asyncio
import os

from datetime import datetime

import sqlalchemy

from sqlalchemy import dialects

from vims.app.auth import PasswordContext, password
from vims.app.config import user_config
from vims.app.database import database
from vims.app.database.models import (
    dashboards,
    datasets,
    datasources,
    groups,
    metadata,
    users,
    visualizations,
)
from vims.app.model import Group, UserPassword
from vims.app.user import synchronize_roles
from vims.core import Dependency, Inject, getLogger, logging_init

log = getLogger("init")
app_config = user_config()


async def setup(password: PasswordContext = Inject(password)):
    now = datetime.utcnow()
    dialect = dialects.sqlite.dialect()

    admin_username = "admin"
    admin_email = "admin@bitbucket.sages.org"
    admin_password = password.hash(os.urandom(32))
    print(f"Admin Password: {admin_password}")
    remote_username = "remote"
    remote_email = "remote@bitbucket.sages.org"
    remote_password = password.hash(os.urandom(32))
    print(f"Remote Password (only need if using remote): {remote_password}")

    log.info("Create admin user")

    admin = UserPassword(
        first_name="Admin",
        last_name="User",
        email=admin_email,
        username=admin_username,
        phone_number="",
        password=admin_password,
        password_last_updated=now,
        password_history=[admin_password],
        roles={"admin": True},
        created=now,
        last_modified=now,
    )

    await Dependency.resolve(synchronize_roles, admin)

    log.info("Create VIMS all users group")
    group = Group(
        group_name="VIMS all users",
        last_modified=now,
        last_modified_by_user=admin.id,
        created=now,
        created_by_user=admin.id,
    )

    remote = UserPassword(
        first_name="Remote",
        last_name="User",
        email=remote_email,
        username=remote_username,
        phone_number="",
        password=remote_password,
        password_last_updated=now,
        password_history=[remote_password],
        roles={"user": True},
        created=now,
        last_modified=now,
        remote=True,
    )

    await Dependency.resolve(synchronize_roles, remote)

    for table in metadata.tables.values():
        # Set `if_not_exists=False` if you want the query to throw an
        # exception when the table already exists
        schema = sqlalchemy.schema.CreateTable(table, if_not_exists=True)
        query = str(schema.compile(dialect=dialect))
        await database.execute(query=query)
    query = users.delete().where(users.c.username == admin.username)
    await database.execute(query)
    query = users.delete().where(users.c.username == remote.username)
    await database.execute(query)

    query = users.insert()
    await database.execute(query, admin.dict())

    query = users.insert()
    await database.execute(query, remote.dict())

    query = groups.delete().where(groups.c.group_name == group.group_name)
    await database.execute(query)

    query = groups.insert()
    await database.execute(query, group.dict())

    query = datasources.delete()
    await database.execute(query)

    query = datasets.delete()
    await database.execute(query)

    query = dashboards.delete()
    await database.execute(query)

    query = visualizations.delete()
    await database.execute(query)


async def main():
    await Dependency.resolve(setup)


logging_init()
asyncio.run(main())
