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

import sys

from datetime import datetime
from uuid import uuid4

from cryptography.fernet import MultiFernet
from fastapi import APIRouter, Depends, HTTPException, status

from vims.core import Config, Dependency, Inject, Reference
from vims.databridge import DataBridgeType
from vims.databridge.sql_alchemy import SqlAlchemyBridge
from vims.databridge.vims import VimsBridge

from ..auth import Permission, get_current_user, require_permission
from ..database import database
from ..database.models import datasources
from ..model import (
    DatasetQuery,
    Datasource,
    DatasourceConnectionInfo,
    DatasourceCreate,
    DatasourceInternal,
    DatasourceRecordDelete,
    DatasourceRecordUpsert,
    DatasourceUpdate,
    User,
)
from ..settings import Settings


def datasource(config=Inject(Config)):
    router = APIRouter()

    MSG_NO_DATASOURCE_FOUND = "No datasource found"

    @router.get(
        "",
        summary="Get Datasources",
        status_code=status.HTTP_200_OK,
        response_model=List[Datasource],
        dependencies=[Depends(require_permission(Permission.READ_DATASOURCES))],
    )
    async def get_datasources(skip: int = 0, limit: int = 10):
        query = datasources.select()
        all_datasources = await database.fetch_all(query)
        ds_list = []

        for ds in all_datasources:
            ds_list.append(Datasource.from_orm(ds))

        return ds_list

    @router.post(
        "",
        summary="Create Datasource",
        status_code=status.HTTP_201_CREATED,
        response_model=Datasource,
        dependencies=[Depends(require_permission(Permission.CREATE_DATASOURCE))],
    )
    async def create_datasource(
        datasource: DatasourceCreate, user: User = Depends(get_current_user)
    ):
        token = str(uuid4())
        now = datetime.utcnow()
        fernet = MultiFernet(config.get(Settings.ENCRYPTION_KEYS))
        encrypted_password = fernet.encrypt(
            bytes(datasource.password, sys.getdefaultencoding())
        ).decode(sys.getdefaultencoding())

        create_datasource = DatasourceConnectionInfo(
            **datasource.dict(exclude={"password"}),
            password=encrypted_password,
            token=token,
            last_modified=now,
            last_modified_by_user=user.id,
            created=now,
            created_by_user=user.id,
        )
        query = datasources.insert()

        create_datasource_dict = create_datasource.dict()
        kwargs = {}
        if datasource.datasource_type == DataBridgeType.SQL_ALCHEMY.value:
            kwargs["ssl"] = datasource.ssl
            kwargs["min_connection_size"] = datasource.min_connection_size
            kwargs["max_connection_size"] = datasource.max_connection_size
            databridge = SqlAlchemyBridge(
                url=datasource.url,
                password=datasource.password,
                ssl=datasource.ssl,
                min_size=datasource.min_connection_size,
                max_size=datasource.max_connection_size,
            )
        else:
            kwargs["username"] = datasource.username
            databridge = VimsBridge(
                url=datasource.url,
                password=datasource.password,
                username=datasource.username,
            )

        del create_datasource_dict["ssl"]
        del create_datasource_dict["min_connection_size"]
        del create_datasource_dict["max_connection_size"]
        del create_datasource_dict["username"]
        create_datasource_dict["kwargs"] = kwargs

        await database.execute(query, create_datasource_dict)

        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        await databridge.connect()
        databridge_manager.add_databridge(token, databridge)

        query = datasources.select().where(datasources.c.id == create_datasource.id)
        created_datasource = await database.fetch_one(query)

        return Datasource.from_orm(created_datasource)

    @router.post(
        "/test",
        summary="Test Datasource",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_permission(Permission.CREATE_DATASOURCE))],
    )
    async def test_datasource_connection(
        datasource: DatasourceCreate,
    ):
        if datasource.datasource_type == DataBridgeType.SQL_ALCHEMY.value:
            databridge = SqlAlchemyBridge(
                url=datasource.url,
                password=datasource.password,
                ssl=datasource.ssl,
                min_size=datasource.min_connection_size,
                max_size=datasource.max_connection_size,
            )
        else:
            databridge = VimsBridge(
                url=datasource.url,
                password=datasource.password,
                username=datasource.username,
            )
        await databridge.connect()
        ping = await databridge.ping()
        await databridge.disconnect()
        return ping

    @router.get(
        "/{datasource_id}",
        summary="Get Datasource",
        status_code=status.HTTP_200_OK,
        response_model=Datasource,
        dependencies=[Depends(require_permission(Permission.READ_DATASOURCE))],
    )
    # TODO-PERMISSION: check that logged in user can get the given datasource.
    async def get_datasource(datasource_id: str):
        query = datasources.select().where(datasources.c.id == datasource_id)
        datasource = await database.fetch_one(query)
        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MSG_NO_DATASOURCE_FOUND,
            )
        return Datasource.from_orm(datasource)

    @router.put(
        "/{datasource_id}",
        summary="Update Datasource",
        status_code=status.HTTP_200_OK,
        response_model=Datasource,
        dependencies=[Depends(require_permission(Permission.UPDATE_DATASOURCE))],
    )
    # TODO-PERMISSION: check that logged in user can update the given datasource.
    async def update_datasource(
        datasource_id: str,
        update: DatasourceUpdate,
        user: User = Depends(get_current_user),
    ):
        now = datetime.utcnow()
        # TODO: test that this endpoint wors
        update_datasource = DatasourceInternal(
            **update,
            last_modified=now,
            last_modified_by_user=user.id,
        )
        query = datasources.update().where(datasources.c.id == datasource_id)
        result = await database.execute(query, update_datasource.dict())

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MSG_NO_DATASOURCE_FOUND,
            )
        query = datasources.select().where(datasources.c.id == datasource_id)
        datasource = await database.fetch_one(query)

        return Datasource.from_orm(datasource)

    @router.delete(
        "/{datasource_id}",
        summary="Delete Datasource",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_permission(Permission.DELETE_DATASOURCE))],
    )
    # TODO-PERMISSION: check that logged in user can delete the given datasource.
    async def delete_datasource(datasource_id: str):
        query = datasources.delete().where(datasources.c.id == datasource_id)
        result = await database.execute(query)

        # TODO: test that this endpoint works.
        # TODO: datasets should be deleted as well.
        if result.deleted_count != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

    @router.get(
        "/{datasource_id}/datasets",
        summary="Get Datasource Dataset Names",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_permission(Permission.GET_DATASOURCE_DATASETS))],
    )
    # TODO-PERMISSION: check that logged in user can view datasets for the given
    #  datasource.
    async def get_datasource_datasets(datasource_id: str):
        query = datasources.select().where(datasources.c.id == datasource_id)
        datasource = await database.fetch_one(query)

        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        databridge = databridge_manager.get_databridge(datasource.token)

        if databridge is None:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )
        result = await databridge.list_datasets()
        return [result]

    @router.get(
        "/{datasource_id}/health",
        summary="Get Datasource Health Status",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_permission(Permission.READ_DATASOURCE))],
    )
    async def get_datasource_health(datasource_id: str):
        query = datasources.select().where(datasources.c.id == datasource_id)
        datasource = await database.fetch_one(query)

        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )
        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        databridge = databridge_manager.get_databridge(datasource.token)
        if databridge is None:
            result = False
        else:
            result = await databridge.ping()
        return result

    @router.post(
        "/{datasource_id}/datasets/{dataset_name}/update_record",
        summary="Create or update a row for a table in the given datasource",
        status_code=status.HTTP_200_OK,
        # TODO: dependencies/permissions
    )
    async def table_record_upsert(
        datasource_id: str,
        dataset_name: str,
        record: DatasourceRecordUpsert,
        user: User = Depends(get_current_user),
    ):
        query = datasources.select().where(datasources.c.id == datasource_id)
        datasource = await database.fetch_one(query)

        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        databridge = databridge_manager.get_databridge(datasource.token)

        if databridge is None:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        metadata = await databridge.get_dataset_fields(dataset_name)
        fields = metadata["fields"]
        pk_exists = await databridge.record_exists(
            dataset_name,
            fields,
            record.primary_key_field,
            record.record[record.primary_key_field],
        )
        if pk_exists:
            result = await databridge.update_record(
                dataset_name,
                fields,
                record.record,
                record.primary_key_field,
                record.record[record.primary_key_field],
            )
        else:
            result = await databridge.create_record(dataset_name, fields, record.record)

        return result

    @router.post(
        "/{datasource_id}/datasets/{dataset_name}/delete_record",
        summary="Delete a row for a table in the given datasource",
        status_code=status.HTTP_200_OK,
        # TODO: dependencies/permissions
    )
    async def table_record_delete(
        datasource_id: str,
        dataset_name: str,
        record: DatasourceRecordDelete,
        user: User = Depends(get_current_user),
    ):
        query = datasources.select().where(datasources.c.id == datasource_id)
        datasource = await database.fetch_one(query)

        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        databridge = databridge_manager.get_databridge(datasource.token)

        if databridge is None:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        metadata = await databridge.get_dataset_fields(dataset_name)
        fields = metadata["fields"]
        result = await databridge.delete_record(
            dataset_name,
            fields,
            record.primary_key_field,
            record.primary_key_value,
        )
        return result

    @router.get(
        "/{datasource_id}/datasets/{dataset_name}/fields",
        summary="Get Fields for a Datasource Dataset",
        status_code=status.HTTP_200_OK,
        dependencies=[
            Depends(require_permission(Permission.GET_DATASOURCE_DATASET_FIELDS))
        ],
    )
    # TODO-PERMISSION: check that logged in user can view datasets for the given
    #  datasource.
    async def get_datasource_datasets_fields(
        datasource_id: str,
        dataset_name: str,
    ):
        query = datasources.select().where(datasources.c.id == datasource_id)
        datasource = await database.fetch_one(query)

        if not datasource:  # or not data_bridges.get(datasource.token, False):
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        databridge = databridge_manager.get_databridge(datasource.token)

        if databridge is None:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        result = await databridge.get_dataset_fields(dataset_name)
        return [result]

    @router.get(
        "/{datasource_id}/datasets/{dataset_name}/{field_name}/values",
        summary="Get unique values for a field in a Datasource Dataset",
        status_code=status.HTTP_200_OK,
        dependencies=[
            Depends(require_permission(Permission.GET_DATASOURCE_DATASET_FIELDS))
        ],
    )
    # TODO-PERMISSION: check that logged in user can view datasets for the given
    #  datasource.
    async def get_datasource_datasets_field_values(
        datasource_id: str,
        dataset_name: str,
        field_name: str,
    ):
        query = datasources.select().where(datasources.c.id == datasource_id)
        datasource = await database.fetch_one(query)

        if not datasource:  # or not data_bridges.get(datasource.token, False):
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        databridge = databridge_manager.get_databridge(datasource.token)

        if databridge is None:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        result = await databridge.get_dataset_field_values(dataset_name, field_name)
        return [result]

    @router.post(
        "/{datasource_id}/datasets/{dataset_name}/query",
        summary="Query a Datasource Dataset",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_permission(Permission.READ_DATASOURCES))],
    )
    # TODO-PERMISSION: check that logged in user can view datasets for the given
    #  datasource.
    async def query_datasource(
        datasource_id: str,
        dataset_name: str,
        dataset_metadata: Dict[str, str],
        query: DatasetQuery,
    ):
        ds_query = datasources.select().where(datasources.c.id == datasource_id)
        datasource = await database.fetch_one(ds_query)
        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        enriched_query = query.dict()
        enriched_query.update(
            {
                "dataset": {
                    "name": dataset_name,
                    "fields": dataset_metadata,
                }
            }
        )

        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        databridge = databridge_manager.get_databridge(datasource.token)

        if databridge is None:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail=MSG_NO_DATASOURCE_FOUND,
            )

        result = await databridge.query(enriched_query)
        return [result]

    return router
