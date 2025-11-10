#  Copyright (c) 2012-2025. The Johns Hopkins University Applied Physics Laboratory LLC
#
#

import os

from datetime import timedelta

from cryptography.fernet import Fernet

from vims.app.settings import Settings
from vims.core import Config

Config.set(Settings.HOST, "0.0.0.0")
Config.set(Settings.PORT, 8084)
Config.set(Settings.RUN_MODE, "standalone")
Config.set(
    Settings.DATABASE_URL,
    os.environ.get("VIMS_DATABASE_URL", "sqlite+aiosqlite:///sages.db"),
)
Config.set(Settings.DATABASE_NAME, "vims")
Config.set(Settings.TOKEN_EXPIRES, timedelta(minutes=60))
Config.set(
    Settings.JWT_SECRET_KEY,
    "6e7514c8a0da6c1901e1856a9cf44b8f5f03ed728f1a876bb35163a55301a3d2",
)
Config.set(Settings.JWT_ALGORITHM, "HS256")
Config.set(
    Settings.ENCRYPTION_KEYS,
    [
        Fernet(b"GgIT3oOvrBDcuEqZcwhtIqMyhsCUzOKDJ0XumB8Zgww="),
    ],
)
Config.set(Settings.ETL_DATA_FOLDER, "etl-data")
Config.set(Settings.ETL_CONNECTION_URL, "sqlite+aiosqlite:///sages.db")
Config.set(Settings.ETL_PRIMARY_KEY_COLUMN_NAME, "vims_primary_key")
