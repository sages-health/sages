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

from typing import List

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from vims.app.database.models import dashboards

from ..auth import Permission, require_permission
from ..database import database
from ..model import Dashboard
from ..model.dashboard import DashboardBase, DashboardInternal, DashboardUpdate


async def dashboard():
    router = APIRouter()

    @router.get(
        "",
        response_model=List[Dashboard],
        dependencies=[Depends(require_permission(Permission.READ_DASHBOARD))],
    )
    async def get_dashboards(skip: int = 0, limit: int = 10):
        query = dashboards.select().limit(limit).offset(skip)
        all_dashboards = await database.fetch_all(query)

        dashboards_list = []
        for ds in all_dashboards:
            min_ds = Dashboard.from_orm(ds)
            min_ds.visualizations = []
            dashboards_list.append(min_ds)

        return dashboards_list

    @router.post(
        "",
        response_model=Dashboard,
        dependencies=[Depends(require_permission(Permission.CREATE_DASHBOARD))],
    )
    async def create_dashboard(dashboard: DashboardBase):
        now = datetime.utcnow()

        try:
            dashboard_to_create = Dashboard(
                **dashboard.dict(by_alias=True), created=now, last_modified=now
            )

            query = dashboards.insert()
            await database.execute(query, dashboard_to_create.dict())

            query = dashboards.select().where(dashboards.c.id == dashboard_to_create.id)
            created_dashboard = await database.fetch_one(query)

            return Dashboard.from_orm(created_dashboard)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dashboard already exists",
            )

    @router.get(
        "/{dashboard_id}",
        response_model=Dashboard,
        dependencies=[Depends(require_permission(Permission.READ_DASHBOARD))],
    )
    async def get_dashboard(dashboard_id):
        query = dashboards.select().where(dashboards.c.id == dashboard_id)
        ds = await database.fetch_one(query)
        if not ds:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No dashboard found for ID",
            )
        return Dashboard.from_orm(ds)

    @router.put(
        "/{dashboard_id}",
        response_model=Dashboard,
        dependencies=[Depends(require_permission(Permission.UPDATE_DASHBOARD))],
    )
    async def update_dashboard(dashboard_id, update: DashboardUpdate):
        now = datetime.utcnow()

        query = dashboards.select().where(dashboards.c.id == dashboard_id)
        ds = await database.fetch_one(query)
        if ds is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dashboard"
            )

        dashboard_to_update = DashboardInternal(
            **update.dict(by_alias=True), last_modified=now
        )

        query = dashboards.update().where(dashboards.c.id == dashboard_id)
        result = await database.execute(query, dashboard_to_update.dict())

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No user found"
            )

        query = dashboards.select().where(dashboards.c.id == dashboard_id)
        ds = await database.fetch_one(query)

        return Dashboard.from_orm(ds)

    @router.delete(
        "/{dashboard_id}",
        dependencies=[Depends(require_permission(Permission.DELETE_DASHBOARD))],
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def delete_dashboard(dashboard_id):
        query = dashboards.delete().where(dashboards.c.id == dashboard_id)
        result = await database.execute(query)
        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No dashboard found",
            )
        return {}

    return router
