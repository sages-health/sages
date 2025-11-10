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
from itertools import islice, tee
from statistics import mean, stdev

from fastapi import APIRouter, Depends, HTTPException, status

from vims.core import Dependency, Reference
from vims.databridge import DataBridgeType
from vims.util import AgeUnitEnum, append_date_part, append_epiweek

from ..auth import Permission, get_current_user, require_permission
from ..database import database
from ..database.models import datasets, datasources
from ..model import (
    DataList,
    Dataset,
    DatasetAdmin,
    DatasetAdminInternal,
    DatasetBaseQuery,
    DatasetQuery,
    User,
)


def align_dataset_on_base_query(dataset):
    """
    Function that takes a dataset and re-works the final fields to be
    displayed to the end user based on the projection and allowed
    reference values
    """
    final_fields = []
    # retrieve existing projection from base_query to determine whether
    # fields can be shown
    projections = dataset.base_query.projection
    for field in dataset.fields:
        # if field is present in projections, then it is allowed to be seen by user
        if projections[field.data_field_name]:
            final_values = []

            """
            if values (reference field) are defined, then
            filter down possible multi-select values
            """
            if len(field.values) > 0 and dataset.base_query.request:
                for filtered_field in dataset.base_query.request["$and"]:
                    """
                    find field in base dataset definition and
                    retrieve the allowed reference values for the field
                    """
                    if list(filtered_field.keys())[0] == field.data_field_name:
                        final_values = filtered_field[field.data_field_name]["$in"]

            # re-assign values and fields back for final dataset representation
            field.values = final_values
            final_fields.append(field)

    return final_fields


async def dataset_accessible(dataset, user):
    user_permissions = list(map(lambda p: Permission(p), user.permissions.keys()))
    if (
        Permission.ADMIN in user_permissions
        or Permission.READ_DATASETS_ALL in user_permissions
    ):
        return True
    elif dataset.groups is None:
        return False
    elif len(set(dataset.groups).intersection(set(user.groups))) > 0:
        # Don't allow remote users to see remote datasets.
        if user.remote:
            datasource_query = datasources.select().where(
                datasources.c.id == dataset.datasource_id
            )
            datasource = await database.fetch_one(datasource_query)
            if datasource and datasource.datasource_type != DataBridgeType.VIMS.value:
                return True
        else:
            return True

    return False


def dataset():
    router = APIRouter()

    NO_DATASET_FOUND = "No dataset found"
    NO_FIELD_REGION_MAPPING_FOUND = "No field region mapping found"

    @router.get(
        "",
        summary="Get Datasets",
        status_code=status.HTTP_200_OK,
        response_model=List[Dataset],
        dependencies=[
            Depends(
                require_permission(
                    [Permission.READ_DATASETS_ALL, Permission.READ_DATASETS_SHARED]
                )
            )
        ],
    )
    async def get_datasets(
        skip: int = 0,
        limit: int = 10,
        datasource_id=None,
        user: User = Depends(get_current_user),
    ):

        query = datasets.select().limit(limit).offset(skip)
        if datasource_id:
            query = query.where(datasets.c.datasource_id == datasource_id)

        all_datasets = await database.fetch_all(query)
        datasets_list = []

        # filter out datasets user does not have access to
        for ds in all_datasets:
            dataset = DatasetAdmin.from_orm(ds)
            dataset.fields = align_dataset_on_base_query(dataset)
            accessible = await dataset_accessible(dataset, user)
            if accessible:
                datasets_list.append(dataset)

        return datasets_list

    @router.get(
        "/{dataset_id}",
        summary="Get Dataset",
        status_code=status.HTTP_200_OK,
        response_model=Dataset,
        dependencies=[
            Depends(
                require_permission(
                    [Permission.READ_DATASET_ALL, Permission.READ_DATASET_SHARED]
                )
            )
        ],
    )
    async def get_dataset(dataset_id: str, user: User = Depends(get_current_user)):
        query = datasets.select().where(datasets.c.id == dataset_id)
        dataset = await database.fetch_one(query)

        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )

        accessible = await dataset_accessible(dataset, user)
        if not accessible:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )

        parsed_dataset = DatasetAdmin.from_orm(dataset)
        parsed_dataset.fields = align_dataset_on_base_query(parsed_dataset)
        return parsed_dataset

    @router.get(
        "/manage",
        summary="Get Datasets",
        status_code=status.HTTP_200_OK,
        response_model=List[DatasetAdmin],
        dependencies=[
            Depends(
                require_permission(
                    [
                        Permission.READ_DATASET_ALL,
                        Permission.CREATE_DATASET,
                        Permission.UPDATE_DATASET,
                    ]
                )
            )
        ],
    )
    async def get_datasets_manage(
        skip: int = 0,
        limit: int = 0,
        datasource_id=None,
        user: User = Depends(get_current_user),
    ):
        user_permissions = list(map(lambda p: Permission(p), user.permissions.keys()))

        query = datasets.select().limit(limit).offset(skip)
        if datasource_id:
            query.where(datasources.c.datasource_id == datasource_id)

        if (
            Permission.READ_DATASETS_ALL in user_permissions
            or Permission.ADMIN in user_permissions
        ):
            pass

        all_datasets = await database.fetch_all(query)

        ds_list = []
        async for ds in all_datasets:
            ds_list.append(DatasetAdmin.from_orm(ds))

        return ds_list

    @router.get(
        "/manage/{dataset_id}",
        summary="Get Dataset",
        status_code=status.HTTP_200_OK,
        response_model=DatasetAdmin,
        dependencies=[
            Depends(
                require_permission(
                    [
                        Permission.READ_DATASET_ALL,
                        Permission.CREATE_DATASET,
                        Permission.UPDATE_DATASET,
                    ]
                )
            )
        ],
    )
    async def get_dataset_manage(
        dataset_id: str, user: User = Depends(get_current_user)
    ):
        user_permissions = list(map(lambda p: Permission(p), user.permissions.keys()))
        if (
            Permission.READ_DATASET_ALL in user_permissions
            or Permission.ADMIN in user_permissions
        ):
            pass
        query = datasets.select().where(datasets.c.id == dataset_id)
        ds = await database.fetch_one(query)

        if not ds:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )
        return DatasetAdmin.from_orm(ds)

    @router.post(
        "",
        summary="Create Dataset",
        status_code=status.HTTP_201_CREATED,
        response_model=DatasetAdmin,
        dependencies=[Depends(require_permission(Permission.CREATE_DATASET))],
    )
    async def create_dataset(
        dataset: DatasetBaseQuery, user: User = Depends(get_current_user)
    ):
        now = datetime.utcnow()
        dataset_to_create = DatasetAdmin(
            **dataset.dict(),
            last_modified=now,
            last_modified_by_user=user.id,
            created=now,
            created_by_user=user.id,
        )

        query = datasets.insert()
        await database.execute(query, dataset_to_create.dict())

        query = datasets.select().where(datasets.c.id == dataset_to_create.id)
        dataset = await database.fetch_one(query)

        return Dataset.from_orm(dataset)

    @router.get(
        "/{dataset_id}/{field_name}/region_mapping",
        summary="Get Region Mappings for a specific dataset field",
        status_code=status.HTTP_200_OK,
        dependencies=[
            Depends(
                require_permission(
                    [Permission.READ_DATASET_ALL, Permission.READ_DATASET_SHARED]
                )
            )
        ],
    )
    async def get_dataset_field_region_mapping(
        dataset_id: str, field_name: str, user: User = Depends(get_current_user)
    ):
        query = datasets.select().where(datasets.c.id == dataset_id)
        dataset = await database.fetch_one(query)

        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )

        accessible = await dataset_accessible(dataset, user)
        if not accessible:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )

        field = list(
            filter(lambda x: x["data_field_name"] == field_name, dataset.fields)
        )
        if len(field) != 1 or len(field[0]["region_map_mapping"]) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=NO_FIELD_REGION_MAPPING_FOUND,
            )

        return field[0]["region_map_mapping"]

    @router.put(
        "/{dataset_id}",
        summary="Update Dataset",
        status_code=status.HTTP_200_OK,
        response_model=DatasetAdmin,
        dependencies=[Depends(require_permission(Permission.UPDATE_DATASET))],
    )
    async def update_dataset(
        dataset_id: str,
        dataset_update: DatasetBaseQuery,
        user: User = Depends(get_current_user),
    ):
        now = datetime.utcnow()

        dataset_to_update = DatasetAdminInternal(
            **dataset_update.dict(by_alias=True),
            last_modified=now,
            last_modified_by_user=user.id,
            id=dataset_id,
        )
        query = datasets.update().where(datasets.c.id == dataset_id)
        result = await database.execute(query, dataset_to_update.dict())

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )

        query = datasets.select().where(datasets.c.id == dataset_id)
        dataset = await database.fetch_one(query)

        return Dataset.from_orm(dataset)

    @router.delete(
        "/{dataset_id}",
        summary="Delete Dataset",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_permission(Permission.DELETE_DATASET))],
    )
    async def delete_dataset(dataset_id: str):
        query = datasets.delete().where(datasets.c.id == dataset_id)
        result = await database.execute(query)

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )

    @router.get(
        "/{dataset_id}/{field_name}/values",
        status_code=status.HTTP_200_OK,
        dependencies=[
            Depends(
                require_permission(
                    [Permission.READ_DATASET_ALL, Permission.READ_DATASET_SHARED]
                )
            )
        ],
    )
    async def dataset_get_field_values(
        dataset_id: str,
        field_name: str,
        user: User = Depends(get_current_user),
    ):
        dataset_query = datasets.select().where(datasets.c.id == dataset_id)
        dataset = await database.fetch_one(dataset_query)

        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )

        accessible = await dataset_accessible(dataset, user)
        if not accessible:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )

        dataset = dataset._mapping
        valid_fields = list(map(lambda f: f["data_field_name"], dataset["fields"]))
        if field_name not in valid_fields:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Field: {field_name} does not exist in the dataset.",
            )

        datasource_query = datasources.select().where(
            datasources.c.id == dataset.datasource_id
        )
        datasource = await database.fetch_one(datasource_query)

        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset contains invalid datasource_id.",
            )

        # Adding dataset metadata required by the worker to process the request.
        datasource = datasource._mapping

        query = {
            "dataset": {
                "name": dataset["dataset_name"],
                "fields": {
                    f["data_field_name"]: f["data_field_type"]
                    for f in dataset["fields"]
                },
                "date_field": dataset["date_field"]
                if "date_field" in dataset
                else None,
            },
            "request": dataset["base_query"]["request"],
            "distinct_field": field_name,
        }

        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        databridge = databridge_manager.get_databridge(datasource.token)

        if databridge is None:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail="Datasource not found",
            )

        result = await databridge.query(query)
        return result

    @router.post(
        "/{dataset_id}/query",
        status_code=status.HTTP_200_OK,
        dependencies=[
            Depends(
                require_permission(
                    [Permission.READ_DATASET_ALL, Permission.READ_DATASET_SHARED]
                )
            )
        ],
    )
    async def data_query(
        dataset_id: str,
        query: DatasetQuery,
        user: User = Depends(get_current_user),
    ):
        dataset_query = datasets.select().where(datasets.c.id == dataset_id)
        dataset = await database.fetch_one(dataset_query)

        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )

        accessible = await dataset_accessible(dataset, user)
        if not accessible:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATASET_FOUND
            )

        datasource_query = datasources.select().where(
            datasources.c.id == dataset.datasource_id
        )
        datasource = await database.fetch_one(datasource_query)

        if not datasource:  # or not data_bridges.get(datasource.token, False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset contains invalid datasource_id.",
            )

        # Adding dataset metadata required by the worker to process the request.
        dataset = dataset._mapping
        datasource = datasource._mapping
        enriched_query = query.dict()
        enriched_query.update(
            {
                "dataset": {
                    "name": dataset["dataset_name"],
                    "fields": {
                        f["data_field_name"]: f["data_field_type"]
                        for f in dataset["fields"]
                    },
                    "date_field": dataset["date_field"]
                    if "date_field" in dataset
                    else None,
                }
            }
        )

        full_request = None

        if dataset["base_query"]["request"] is not None or query.request is not None:
            full_request = {"$and": []}

        if dataset["base_query"]["request"] is not None:
            full_request["$and"].append(dataset["base_query"]["request"])

        if query.request is not None:
            full_request["$and"].append(query.request)

        full_projection = dataset["base_query"]["projection"]
        if query.projection:
            projection_keys = set(query.projection.keys())
            for key in projection_keys:
                if key in full_projection:
                    query.projection[key] = full_projection[key]
                else:
                    del query.projection[key]

            full_projection = query.projection

        enriched_query.update({"request": full_request, "projection": full_projection})

        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        databridge = databridge_manager.get_databridge(datasource["token"])

        if databridge is None:
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST,
                detail="Datasource not found",
            )
        result = await databridge.query(enriched_query)

        if (
            "transformations" in enriched_query
            and enriched_query["transformations"] is not None
        ):
            transformation_type = enriched_query.get("transformations", {}).get(
                "transformation_type"
            )

            transformation_cols = set(
                [
                    col
                    for col in enriched_query.get("transformations", {}).get(
                        "transformation_columns", []
                    )
                ]
            )

            aggregation_cols = (
                enriched_query.get("transformations", {})
                .get("aggregate", {})
                .get("group_by", {})
                .get("field")
            )
            count_col = (
                enriched_query.get("transformations", {})
                .get("aggregate", {})
                .get("group_by", {})
                .get("aggregators", {})
                .get("count", {})
                .get("field")
            )
            agg_func = (
                enriched_query.get("transformations", {})
                .get("aggregate", {})
                .get("group_by", {})
                .get("aggregators", {})
                .get("count", {})
                .get("function")
            )

            drop_existing = enriched_query.get("transformations", {}).get(
                "drop_existing", {}
            )

            if transformation_type == "epiweek":
                result["values"] = append_epiweek(
                    result["values"],
                    date_cols=transformation_cols,
                    aggregate_cols=aggregation_cols,
                    count_col=count_col,
                    agg_func=agg_func,
                    drop_existing=drop_existing,
                )
            elif transformation_type in ("month", "day", "year", "week"):
                result["values"] = append_date_part(
                    result["values"],
                    date_cols=transformation_cols,
                    aggregate_cols=aggregation_cols,
                    count_col=count_col,
                    agg_func=agg_func,
                    date_part=transformation_type,
                    drop_existing=drop_existing,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Un-allowed transformation specified",
                )

        # Determines which variant of age exist in dictionary's keys
        age_variants = ["Edad", "edad", "EDAD"]
        found_age = ""
        for i in range(len(result["values"])):
            temp_list = list(result["values"][i].keys())
            for j in range(len(temp_list)):
                if temp_list[j] == age_variants[0]:
                    found_age = age_variants[0]
                    break
                elif temp_list[j] == age_variants[1]:
                    found_age = age_variants[1]
                    break
                elif temp_list[j] == age_variants[2]:
                    found_age = age_variants[2]
                    break
                else:
                    continue
            if found_age != "":
                break

        # Categorize ages based on best units for display
        for i in range(len(result["values"])):
            if found_age != "":
                age_data = result["values"][i][found_age]
                if age_data:
                    if type(age_data) is int or age_data.is_integer():
                        temp = str(int(result["values"][i][found_age]))
                        result["values"][i][found_age] = temp + AgeUnitEnum.YEARS
                    elif round(age_data * 12, 4).is_integer():
                        temp = str(int(round(age_data * 12, 4)))
                        result["values"][i][found_age] = temp + AgeUnitEnum.MONTHS
                    elif round(age_data * 365, 4).is_integer():
                        temp = str(int(round(age_data * 365, 4)))
                        result["values"][i][found_age] = temp + AgeUnitEnum.DAYS
                    else:
                        continue

        return [result]

    @router.post(
        "/stdev/{num_sigma}/{window}/{start_idx}",
        summary="Get Std Dev",
        status_code=status.HTTP_200_OK,
    )
    async def get_std_dev(
        data: DataList,
        num_sigma: int = 1,
        window: int = 8,
        start_idx: int = 0,
    ):
        return ([None] * (window + start_idx)) + [
            stdev(window) * num_sigma
            for window in zip(
                *[
                    islice(data_iter, i, None)
                    for i, data_iter in enumerate(tee(data.value[start_idx:], window))
                ]
            )
        ]

    @router.post(
        "/delta/{num_prev}",
        summary="Get Delta",
        status_code=status.HTTP_200_OK,
    )
    async def get_delta(
        data: DataList,
        num_prev: int = 1,
    ):
        return [
            v - data.value[i - num_prev] if i >= num_prev else None
            for i, v in enumerate(data.value)
        ]

    @router.post(
        "/sma/{window}/{start_idx}",
        summary="Get sma",
        status_code=status.HTTP_200_OK,
    )
    async def get_sma(
        data: DataList,
        window: int = 8,
        start_idx: int = 0,
    ):
        return ([None] * (window + start_idx)) + [
            mean(window)
            for window in zip(
                *[
                    islice(data_iter, i, None)
                    for i, data_iter in enumerate(tee(data.value[start_idx:], window))
                ]
            )
        ]

    return router
