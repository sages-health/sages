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

from typing import Dict, List

from pathlib import Path

from fastapi import APIRouter, Depends

from vims.core import Inject, getLogger
from vims.util import find_upwards, load_dynamic

from ..auth import Permission, Role, require_permission

log = getLogger(__name__)


def role_config():
    # Load the roles on application startup
    file = find_upwards("roles.config.py", Path(__file__).parent.parent.parent)
    if file:
        module = load_dynamic("role_conf", file)
        roles = getattr(module, "roles", {})
        for role, permissions in roles.items():
            log.info(f"Load role: {role.name}")
            for permission in permissions:
                log.debug(f"  - {permission.name}")
        return roles
    else:
        raise RuntimeError("Unable to load role configuration")


def role(roles: Dict[Role, List[Permission]] = Inject(role_config)):
    router = APIRouter()

    @router.get(
        "",
        response_model=Dict[str, List[str]],
        dependencies=[Depends(require_permission(Permission.READ_ROLES))],
    )
    def get_roles():
        roles_serialize: Dict[str, List[str]] = {}
        for role, permissions in roles.items():
            roles_serialize[role.value] = list(map(lambda p: p.value, permissions))
        return roles_serialize

    return router
