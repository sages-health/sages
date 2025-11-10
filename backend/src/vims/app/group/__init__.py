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

from vims.app.auth import Permission, get_current_user, require_permission
from vims.app.database.models import datasets, groups, users
from vims.app.model import Dataset, Group, GroupBase, GroupInternal, User

from ..database import database


def group():
    router = APIRouter()

    @router.get(
        "",
        summary="Get User Groups",
        status_code=status.HTTP_200_OK,
        response_model=List[Group],
        dependencies=[Depends(require_permission([Permission.READ_GROUPS]))],
    )
    async def get_groups(skip: int = 0, limit: int = 10):
        query = groups.select().limit(limit).offset(skip)
        cursor = await database.fetch_all(query)
        groups_list = []
        for document in cursor:
            groups_list.append(Group.from_orm(document))

        return groups_list

    @router.get(
        "/{group_id}",
        response_model=Group,
        dependencies=[Depends(require_permission(Permission.READ_GROUPS))],
    )
    async def get_group(group_id):
        query = groups.select().where(groups.c.id == group_id)
        group = await database.fetch_one(query)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No group found"
            )
        return Group.from_orm(group)

    @router.post(
        "",
        summary="Create Group",
        status_code=status.HTTP_201_CREATED,
        response_model=Group,
        dependencies=[Depends(require_permission(Permission.CREATE_GROUP))],
    )
    async def create_group(group: GroupBase, user: User = Depends(get_current_user)):
        now = datetime.utcnow()
        group_to_create = Group(
            **group.dict(by_alias=True),
            last_modified=now,
            last_modified_by_user=user.id,
            created=now,
            created_by_user=user.id,
        )

        query = groups.insert()
        await database.execute(query, group_to_create.dict())

        query = groups.select().where(groups.c.id == group_to_create.id)
        created_group = await database.fetch_one(query)

        return Group.from_orm(created_group)

    @router.put(
        "/{group_id}",
        summary="Update User Group",
        status_code=status.HTTP_200_OK,
        response_model=Group,
        dependencies=[Depends(require_permission(Permission.UPDATE_GROUP))],
    )
    async def update_group(
        group_id: str, update: GroupBase, user: User = Depends(get_current_user)
    ):
        now = datetime.utcnow()

        dataset_to_update = GroupInternal(
            **update.dict(by_alias=True),
            last_modified=now,
            last_modified_by_user=user.id,
        )

        query = groups.update().where(groups.c.id == group_id)
        result = await database.execute(query, dataset_to_update.dict())

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="USER GROUP NOT FOUND"
            )

        query = groups.select().where(groups.c.id == group_id)
        created_group = await database.fetch_one(query)

        return Group.from_orm(created_group)

    @router.delete(
        "/{group_id}",
        summary="Delete User Group",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_permission(Permission.DELETE_GROUP))],
    )
    async def delete_group(group_id: str):
        query = groups.delete().where(groups.c.id == group_id)
        result = await database.execute(query)

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="USER GROUP NOT FOUND"
            )

        all_users = await database.fetch_all(users.select())

        for user in all_users:
            if group_id in user.groups:
                user.groups.remove(group_id)
                query = users.update().where(users.c.id == user.id)
                await database.execute(query, user)

        all_datasets = await database.fetch_all(datasets.select())

        for dataset in all_datasets:
            if group_id in dataset.groups:
                dataset.groups.remove(group_id)
                query = datasets.update().where(datasets.c.id == dataset.id)
                await database.execute(query, dataset)

    @router.get(
        "/datasets/{group_id}",
        summary="Get Datasets for User Group",
        status_code=status.HTTP_200_OK,
        response_model=List[Dataset],
        dependencies=[
            Depends(
                require_permission(
                    [Permission.READ_GROUPS, Permission.READ_DATASETS_ALL]
                )
            )
        ],
    )
    async def get_datasets_for_group(group_id: str):
        query = groups.select().where(groups.c.id == group_id)
        group = await database.fetch_one(query)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No group found"
            )
        query = datasets.select()

        all_datasets = await database.fetch_all(query)

        group_datasets = []
        for dataset in all_datasets:
            if group_id in dataset.groups:
                group_datasets.append(dataset)

        return group_datasets

        # async for document in cursor:
        #     datasets.append(DatasetAdmin.parse_obj(document))

        return datasets

    @router.get(
        "/users/{group_id}",
        summary="Get list of users for user group",
        status_code=status.HTTP_200_OK,
        response_model=List[User],
        dependencies=[
            Depends(require_permission([Permission.READ_GROUPS, Permission.READ_USERS]))
        ],
    )
    async def get_users_for_group(group_id: str):
        query = groups.select().where(groups.c.id == group_id)
        group = await database.fetch_one(query)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No group found"
            )

        query = users.select()

        all_users = await database.fetch_all(query)

        group_users = []
        for user in all_users:
            if group_id in user.groups:
                group_users.append(user)

        return group_users

    return router
