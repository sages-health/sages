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

from ..auth import Permission, get_current_user, require_permission
from ..database import database
from ..database.models import maps
from ..model import LimitedRegionMap, RegionMap, RegionMapBase, RegionMapInternal, User


def region_map():
    router = APIRouter()

    MSG_NO_MAP_FOUND = "No map found"

    @router.get(
        "",
        summary="Get Maps",
        status_code=status.HTTP_200_OK,
        response_model=List[LimitedRegionMap],
        dependencies=[Depends(require_permission(Permission.READ_MAPS))],
    )
    async def get_maps():
        query = maps.select()
        results = await database.fetch_all(query)
        maps_list = []
        for result in results:
            maps_list.append(RegionMap.from_orm(result))

        return maps_list

    @router.post(
        "",
        summary="Create Map",
        status_code=status.HTTP_201_CREATED,
        response_model=RegionMap,
        dependencies=[Depends(require_permission(Permission.CREATE_MAP))],
    )
    async def create_map(map: RegionMapBase, user: User = Depends(get_current_user)):
        now = datetime.utcnow()
        map_to_create = RegionMap(
            **map.dict(),
            last_modified=now,
            last_modified_by_user=user.id,
            created=now,
            created_by_user=user.id,
        )

        query = maps.insert()
        await database.execute(query, map_to_create.dict())

        query = maps.select().where(maps.c.id == map_to_create.id)
        created_map = await database.fetch_one(query)

        return RegionMap.from_orm(created_map)

    @router.get(
        "/{map_id}",
        summary="Get Map",
        status_code=status.HTTP_200_OK,
        response_model=RegionMap,
        dependencies=[Depends(require_permission(Permission.READ_MAPS))],
    )
    async def get_map(map_id: str):
        query = maps.select().where(maps.c.id == map_id)
        map = await database.fetch_one(query)
        if not map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MSG_NO_MAP_FOUND,
            )
        return RegionMap.from_orm(map)

    @router.put(
        "/{map_id}",
        summary="Update Map",
        status_code=status.HTTP_200_OK,
        response_model=RegionMap,
        dependencies=[Depends(require_permission(Permission.UPDATE_MAP))],
    )
    async def update_map(
        map_id: str, update: RegionMapBase, user: User = Depends(get_current_user)
    ):
        now = datetime.utcnow()

        map_to_date = RegionMapInternal(
            **update.dict(by_alias=True),
            last_modified=now,
            last_modified_by_user=user.id,
            id=map_id,
        )

        query = maps.update().where(maps.c.id == map_id)
        result = await database.execute(query, map_to_date.dict())

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NO_MAP_FOUND
            )
        query = maps.select().where(maps.c.id == map_to_date.id)
        new_map = await database.fetch_one(query)

        return RegionMap.from_orm(new_map)

    @router.delete(
        "/{map_id}",
        summary="Delete Map",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_permission(Permission.DELETE_MAP))],
    )
    async def delete_map(map_id: str):
        query = maps.delete().where(maps.c.id == map_id)
        result = await database.execute(query)

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=MSG_NO_MAP_FOUND
            )

    return router
