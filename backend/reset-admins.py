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


# flake8: noqa

import asyncio

from sqlalchemy import func

from vims.app.config import user_config
from vims.app.database import database
from vims.app.database.models import user_login_tracking, user_security_settings, users
from vims.app.model import UserLoginTracking, UserPassword, UserSecuritySettings
from vims.core import Dependency, getLogger, logging_init

log = getLogger("init")
app_config = user_config()


async def setup():
    query = users.select().where(func.json_extract(users.c.roles, "$.admin") == True)
    results = await database.fetch_all(query)
    for result in results:
        user = UserPassword.model_validate(result)
        query = user_login_tracking.select().where(
            user_login_tracking.c.user == user.id
        )
        login_tracking = await database.fetch_one(query)
        if login_tracking:
            login_tracking = UserLoginTracking.model_validate(login_tracking)
            login_tracking.locked_until = None
            login_tracking.attempts = 0
            query = user_login_tracking.update().where(
                user_login_tracking.c.user == user.id
            )
            await database.execute(query, login_tracking.model_dump())
        query = user_security_settings.select().where(
            user_security_settings.c.user == user.id
        )
        security_settings = await database.fetch_one(query)
        if security_settings:
            security_settings = UserSecuritySettings.model_validate(security_settings)
            security_settings.otp_enabled = False
            query = user_security_settings.update().where(
                user_security_settings.c.user == user.id
            )
            await database.execute(query, security_settings.model_dump())


async def main():
    await Dependency.resolve(setup)


logging_init()
asyncio.run(main())
