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

from vims.app.database.models import datasets, visualizations

from ..auth import Permission, get_current_user, require_permission
from ..database import database
from ..model import (
    Dataset,
    User,
    Visualization,
    VisualizationBase,
    VisualizationInternal,
)


def visualization():
    router = APIRouter()

    NO_VISUALIZATION_FOUND = "No visualization found"

    @router.get(
        "",
        summary="Get Visualizations",
        status_code=status.HTTP_200_OK,
        response_model=List[Visualization],
        dependencies=[Depends(require_permission(Permission.READ_VISUALIZATIONS))],
    )
    async def get_visualizations(user: User = Depends(get_current_user)):
        query = visualizations.select()
        all_visualizations = await database.fetch_all(query)

        user_permissions = list(map(lambda p: Permission(p), user.permissions.keys()))
        visualizations_list = []

        for viz in all_visualizations:
            if (
                Permission.READ_DATASETS_ALL in user_permissions
                or Permission.ADMIN in user_permissions
            ):
                visualizations_list.append(Visualization.from_orm(viz))
            else:
                # filter out visualizations user does not have access to
                for config in viz["configs"]:

                    query = datasets.select().where(
                        datasets.c.id == config["dataset_id"]
                    )
                    dataset = await database.fetch_one(query)

                    dataset = Dataset.from_orm(dataset)
                    if dataset.groups is None:
                        continue

                    for dsgroup in dataset.groups:
                        match = False
                        for ugroup in user.groups:
                            if dsgroup == ugroup:
                                match = True
                                break
                        if match:
                            visualizations_list.append(Visualization.from_orm(viz))

        return visualizations_list

    @router.post(
        "",
        summary="Create Visualization",
        status_code=status.HTTP_201_CREATED,
        response_model=Visualization,
        dependencies=[Depends(require_permission(Permission.CREATE_VISUALIZATION))],
    )
    async def create_visualization(
        visualization: VisualizationBase, user: User = Depends(get_current_user)
    ):
        now = datetime.utcnow()
        visualization_to_create = Visualization(
            **visualization.dict(),
            last_modified=now,
            last_modified_by_user=user.id,
            created=now,
            created_by_user=user.id,
        )

        query = visualizations.insert()
        await database.execute(query, visualization_to_create.dict())

        query = visualizations.select().where(visualizations.c.id == visualization.id)
        created_visualization = await database.fetch_one(query)

        return Visualization.from_orm(created_visualization)

    @router.get(
        "/{visualization_id}",
        summary="Get Visualization",
        status_code=status.HTTP_200_OK,
        response_model=Visualization,
        dependencies=[Depends(require_permission(Permission.READ_VISUALIZATION))],
    )
    async def get_visualization(
        visualization_id: str, user: User = Depends(get_current_user)
    ):
        query = visualizations.select().where(visualizations.c.id == visualization_id)
        viz = await database.fetch_one(query)

        if not viz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_VISUALIZATION_FOUND
            )

        user_permissions = list(map(lambda p: Permission(p), user.permissions.keys()))

        # filter out visualizations user does not have access to
        for config in viz.configs:
            query = datasets.select().where(datasets.c.id == config["dataset_id"])
            dataset = await database.fetch_one(query)

            dataset = Dataset.from_orm(dataset)
            if (
                Permission.READ_DATASETS_ALL in user_permissions
                or Permission.ADMIN in user_permissions
            ):
                continue
            else:
                if dataset.groups is None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="UNAUTHORIZED",
                    )
                for dsgroup in dataset.groups:
                    match = False
                    for ugroup in user.groups:
                        if dsgroup == ugroup:
                            match = True
                            break
                    if match:
                        break
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="UNAUTHORIZED",
                        )
        return Visualization.from_orm(viz)

    @router.put(
        "/{visualization_id}",
        summary="Update Visualization",
        status_code=status.HTTP_200_OK,
        response_model=Visualization,
        dependencies=[Depends(require_permission(Permission.UPDATE_VISUALIZATION))],
    )
    async def update_visualization(
        visualization_id: str,
        update: VisualizationBase,
        user: User = Depends(get_current_user),
    ):
        now = datetime.utcnow()

        visualization_to_update = VisualizationInternal(
            **update.dict(by_alias=True),
            last_modified=now,
            last_modified_by_user=user.id,
        )
        query = visualizations.update().where(visualizations.c.id == visualization_id)
        result = await database.execute(query, visualization_to_update.dict())

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_VISUALIZATION_FOUND
            )
        query = visualizations.select().where(visualizations.c.id == visualization_id)
        viz = await database.fetch_one(query)

        return Visualization.from_orm(viz)

    @router.delete(
        "/{visualization_id}",
        summary="Delete Visualization",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_permission(Permission.DELETE_VISUALIZATION))],
    )
    async def delete_visualization(visualization_id: str):
        query = visualizations.delete().where(visualizations.c.id == visualization_id)
        result = await database.execute(query)
        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_VISUALIZATION_FOUND
            )

    return router
