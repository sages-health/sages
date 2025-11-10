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

import os

from datetime import timedelta

from cryptography.fernet import Fernet

from vims.app.settings import Settings
from vims.core import Config

Config.set(Settings.ENVIRONMENT, "production")
Config.set(
    Settings.HOST,
    os.environ.get("VIMS_BACKEND_HOST", "backend"),
)
Config.set(
    Settings.PORT,
    int(os.environ.get("VIMS_BACKEND_PORT", 8084)),
)
Config.set(Settings.RUN_MODE, "server")
Config.set(
    Settings.DATABASE_URL,
    os.environ.get("VIMS_DATABASE_URL", "sqlite+aiosqlite:///sages.db"),
)
Config.set(Settings.DATABASE_NAME, "vims")
Config.set(Settings.TOKEN_EXPIRES, timedelta(minutes=60))
Config.set(
    Settings.JWT_SECRET_KEY,
)
Config.set(Settings.JWT_ALGORITHM, "HS256")
Config.set(
    Settings.ENCRYPTION_KEYS,
    [
        # Fernet(b""),
    ],
)
Config.set(Settings.ETL_DATA_FOLDER, "/etl-data")
Config.set(
    Settings.ETL_CONNECTION_URL,
    "sqlite+aiosqlite:///sages.db",
)
Config.set(Settings.ETL_PRIMARY_KEY_COLUMN_NAME, "vims_primary_key")
Config.set(Settings.MOBILE_ETL_ENCRYPTION_KEY, "replaceme")
