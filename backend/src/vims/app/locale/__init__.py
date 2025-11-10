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

from typing import Dict

import json

from pathlib import Path

import aiofiles

from fastapi import APIRouter, HTTPException, status

from vims.util import find_upwards


def locale():

    router = APIRouter()

    @router.get("/{lang}", response_model=Dict[str, Dict[str, str]])
    async def get_locale(lang):
        i18n = f"{lang}".lower()
        locale_file = Path("i18n") / Path(f"{i18n}.json")
        locale_file = find_upwards(locale_file, Path(__file__).parent)
        if not locale_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown locale '{lang}'",
            )

        contents = None
        async with aiofiles.open(locale_file) as f:
            contents = await f.read()
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to read locale file",
            )
        contents = json.loads(contents)
        return contents

    return router
