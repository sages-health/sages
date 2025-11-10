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

from typing import Any, Dict, List, Type

import copy

from datetime import datetime

import sqlalchemy as sqla

from databases import Database, DatabaseURL

from vims.core import getLogger
from vims.databridge import DataBridge
from vims.util import sqla_where_compiler as swc

log = getLogger(__name__)

SQLA_FNS = {
    "max": {
        "fn": sqla.func.max,
        "types": ["int", "float", "datetime"],
        "result_type": "self",
    },
    "min": {
        "fn": sqla.func.min,
        "types": ["int", "float", "datetime"],
        "result_type": "self",
    },
    "sum": {"fn": sqla.func.sum, "types": ["int", "float"], "result_type": "self"},
    "count": {
        "fn": sqla.func.count,
        "types": ["int", "float", "datetime", "str"],
        "result_type": "int",
    },
}


class SqlAlchemyBridge(DataBridge):
    FIELD_TYPES: Dict[str, Type] = {
        "text": str,
        "varchar": str,
        "character varying": str,
        "longtext": str,
        "double": float,
        "numeric": float,
        "int": int,
        "bigint": int,
        "tinyint": int,
        "integer": int,
        "date": datetime,
        "datetime": datetime,
        "float": float,
        "timestamp without time zone": datetime,
        "timestamp": datetime,
    }

    def __init__(
        self,
        url: str = "",
        password: str = "",
        ssl: bool = True,
        min_size: int = 5,
        max_size: int = 20,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.database_url = DatabaseURL(url.format(password=password))
        self.dialect = self.database_url.dialect
        self.database_type = self.dialect
        self.schema = (
            "public" if self.dialect == "postgresql" else self.database_url.database
        )
        if self.dialect == "sqlite":
            self.database = Database(self.database_url)
        elif self.dialect == "mysql":
            self.database = Database(
                self.database_url,
                ssl=ssl,
                min_size=min_size,
                max_size=max_size,
                pool_recycle=1800,
            )
        else:
            self.database = Database(
                self.database_url, ssl=ssl, min_size=min_size, max_size=max_size
            )

    def __str__(self):
        return f"{self.display_name}--{self.database_url}"

    def get_database_type(self):
        return self.database_type

    async def connect(self):
        await self.database.connect()

    async def disconnect(self):
        await self.database.disconnect()

    async def ping(
        self,
    ):
        result = await self.list_datasets()
        return result.get("error") is None

    async def list_datasets(self):
        if self.dialect == "sqlite":
            query = "SELECT name FROM sqlite_master WHERE type = 'table'"
        else:
            query = "SELECT table_name FROM information_schema.tables"
            if len(self.schema) > 0:
                query = f"{query} WHERE table_schema = '{self.schema}'"

        datasets: List[Dict[str, str]] = []
        try:
            async for row in self.database.iterate(query=query):
                table_name = (
                    row["table_name"] if self.dialect in ("postgresql",) else row[0]
                )
                datasets.append({"name": table_name, "display_name": table_name})
            return {"datasets": datasets, "error": None}
        except Exception as e:
            return {"datasets": datasets, "error": str(e)}

    async def get_dataset_fields(self, dataset_name: str):
        fields: Dict[str, str] = {}
        if self.dialect == "sqlite":
            query = f"PRAGMA table_info('{dataset_name}')"
        else:
            query = (
                "SELECT column_name, data_type FROM information_schema.columns "
                f"WHERE table_name = '{dataset_name}'"
            )
            if len(self.schema) > 0:
                query = f"{query} AND table_schema = '{self.schema}'"
        try:
            async for row in self.database.iterate(query=query):
                if self.dialect in ("postgresql",):
                    name = row["column_name"]
                    raw_type = row["data_type"]
                elif self.dialect == "sqlite":
                    name = row[1]
                    raw_type = row[2].lower()
                else:
                    name = row[0]
                    raw_type = row[1]
                fields[name] = self.FIELD_TYPES[raw_type].__name__
            return {"fields": fields, "error": None}
        except Exception as e:
            return {"fields": [], "error": str(e)}

    async def get_dataset_field_values(self, dataset_name: str, field_name: str):
        query = None
        if self.dialect == "postgresql":
            query = f'SELECT DISTINCT "{ field_name}" FROM {self.schema}.{dataset_name}'
        elif len(self.schema) > 0 and self.dialect != "sqlite":
            query = f"SELECT DISTINCT {field_name} FROM {self.schema}.{dataset_name}"
        else:
            query = f"SELECT DISTINCT { field_name} FROM {dataset_name}"

        values: List[str] = []
        try:
            async for row in self.database.iterate(query=query):
                if self.dialect == "postgresql":
                    values.append(row[field_name])
                else:
                    values.append(row[0])
            return {"values": values, "error": None}
        except Exception as e:
            return {"values": values, "error": str(e)}

    async def query(self, query_args: Dict[str, Any]):
        # Copy query args to ensure that we can safely make modifications to it.
        query_args_copy = copy.deepcopy(query_args)
        try:
            (
                dataset_name,
                dataset_metadata,
                selected_fields,
                request,
                limit,
                offset,
                order_by,
                group_by,
                having,
                count_fields,
                distinct_field,
            ) = self.validate_query_args(query_args_copy)

            sqla_columns = {}
            for field_name, field_type in dataset_metadata.items():
                sqla_columns[field_name] = sqla.Column(field_name)

            m = sqla.MetaData()
            sqla.Table(dataset_name, m, *sqla_columns.values())

            group_by_fields = None
            group_by_labels = []
            if group_by is not None:
                group_by_fields = [sqla_columns[f] for f in group_by.get("fields")]
                for agg_label, agg_data in group_by["aggregators"].items():
                    agg_field = agg_data.get("field", None)
                    agg_fn = agg_data["function"]

                    if agg_fn == "count" and agg_field is None:
                        sqla_columns[agg_label] = sqla.func.count().label(agg_label)
                    else:
                        sqla_columns[agg_label] = SQLA_FNS[agg_fn]["fn"](
                            sqla_columns[agg_field]
                        ).label(agg_label)
                    group_by_labels.append(agg_label)

            if group_by_fields is not None:
                sqla_selected_columns = group_by_fields + [
                    sqla_columns[f] for f in group_by_labels
                ]
            elif distinct_field is not None:
                sqla_selected_columns = [sqla_columns[distinct_field].distinct()]
            elif count_fields is not None:
                sqla_selected_columns = [
                    sqla.func.count(sqla_columns[f].distinct()).label(
                        f"count_distinct_{f}"
                    )
                    for f in count_fields
                ]
            elif selected_fields is not None:
                sqla_selected_columns = [sqla_columns[f] for f in selected_fields]
            else:
                sqla_selected_columns = sqla_columns.values()

            q = sqla.select(*sqla_selected_columns)

            if request is not None:
                try:
                    compiled_columns = request.compile(sqla_columns, dataset_metadata)
                    q = q.where(compiled_columns)
                except swc.SqlaWhereCompileError as e:
                    raise RuntimeError(f"Error compiling query request: {str(e)}")

            if group_by_fields is not None:
                q = q.group_by(*group_by_fields)

            if having is not None:
                try:
                    q = q.having(having.compile(sqla_columns, dataset_metadata))
                except swc.SqlaWhereCompileError as e:
                    raise RuntimeError(f"Error compiling query having: {str(e)}")

            if limit is not None:
                q = q.limit(limit)

            if offset is not None:
                q = q.offset(offset)

            if order_by is not None:
                orders = []
                for field_name, order in order_by:
                    column = sqla_columns.get(field_name)
                    orders.append(
                        column.asc() if order.lower() == "asc" else column.desc()
                    )
                q = q.order_by(*orders)

            results = []
            async for row in self.database.iterate(query=q):
                row_dict = {}
                for k in row._mapping.keys():
                    row_dict[k] = row._mapping[k]
                results.append(row_dict)

            # Return the total count for this query.
            q = q.limit(None)
            q = q.offset(None)
            count_q = sqla.select(sqla.func.count()).select_from(q)
            total_count = await self.database.fetch_one(query=count_q)
            total = total_count[0]

            return {"values": results, "total": total, "error": None}
        except Exception as e:
            return {"values": [], "total": -1, "error": str(e)}

    async def record_exists(
        self, table_name, fields, primary_key_field, primary_key_value
    ):
        sqla_columns = {}
        for field_name, field_type in fields.items():
            sqla_columns[field_name] = sqla.Column(field_name)

        metadata = sqla.MetaData()
        table = sqla.Table(table_name, metadata, *sqla_columns.values())

        query = (
            table.select()
            .where(table.c[primary_key_field] == primary_key_value)
            .limit(1)
        )
        result = await self.database.fetch_one(query)

        return result is not None

    async def create_record(self, table_name, fields, record):
        # TODO: check primary key, type checking
        try:
            sqla_columns = {}
            for field_name, field_type in fields.items():
                sqla_columns[field_name] = sqla.Column(field_name)
            metadata = sqla.MetaData()
            table = sqla.Table(table_name, metadata, *sqla_columns.values())

            insert = table.insert().values(**record)
            result = await self.database.execute(insert)
            return {"values": result, "error": None}

        except Exception as e:
            return {"values": [], "total": -1, "error": str(e)}

    async def update_record(
        self, table_name, fields, record, primary_key_field, primary_key_value
    ):
        try:
            sqla_columns = {}
            for field_name, field_type in fields.items():
                sqla_columns[field_name] = sqla.Column(field_name)
            metadata = sqla.MetaData()
            table = sqla.Table(table_name, metadata, *sqla_columns.values())
            update_values = {k: v for k, v in record.items() if k != primary_key_field}
            update_stmt = (
                table.update()
                .where(table.c[primary_key_field] == primary_key_value)
                .values(**update_values)
            )
            result = await self.database.execute(update_stmt)
            return {"values": result, "error": None}

        except Exception as e:
            return {"values": [], "total": -1, "error": str(e)}

    async def delete_record(
        self, table_name, fields, primary_key_field, primary_key_value
    ):
        try:
            sqla_columns = {}
            for field_name, field_type in fields.items():
                sqla_columns[field_name] = sqla.Column(field_name)

            metadata = sqla.MetaData()
            table = sqla.Table(table_name, metadata, *sqla_columns.values())

            delete_stmt = table.delete().where(
                table.c[primary_key_field] == primary_key_value
            )

            result = await self.database.execute(delete_stmt)
            return {"values": result, "error": None}

        except Exception as e:
            return {"values": [], "total": -1, "error": str(e)}

    def validate_query_args(self, args):
        dataset_info = args.get("dataset", None)
        if dataset_info is None:
            raise RuntimeError("No dataset info provided")

        dataset_name = dataset_info.get("name", None)
        if dataset_name is None:
            raise RuntimeError("No dataset name provided")

        dataset_metadata = dataset_info.get("fields", None)
        if dataset_metadata is None:
            raise RuntimeError("No dataset fields provided")
        if not isinstance(dataset_metadata, dict) or len(dataset_metadata) < 1:
            raise RuntimeError("Dataset fields must be a non-empty dict.")

        all_fields = list(dataset_metadata.keys())
        all_valid_fields = []
        projection = args.get("projection", None)
        if projection is not None:
            if not isinstance(projection, dict):
                raise RuntimeError("Projection must be a dict.")
            for field_name, included in projection.items():
                if included and field_name not in all_fields:
                    raise RuntimeError(
                        f"{field_name} is not a field in dataset: {dataset_name}."
                    )
                elif included:
                    all_valid_fields.append(field_name)
        else:
            all_valid_fields = all_fields

        group_by = args.get("group_by", None)
        if group_by is not None:
            if not isinstance(group_by, dict):
                raise RuntimeError("Group_by must be a dictionary.")

            group_by_fields = group_by.get("fields")
            if (
                group_by_fields is None
                or not isinstance(group_by_fields, list)
                or len(group_by_fields) != len(set(group_by_fields))
            ):
                raise RuntimeError("Group_by must contain a unique list of fields.")
            for group_by_field in group_by_fields:
                if group_by_field not in all_valid_fields:
                    raise RuntimeError(
                        f"Group_by field: {group_by_field} is not a valid field."
                    )

            aggregators = group_by.get("aggregators")
            if aggregators is None or not isinstance(aggregators, dict):
                raise RuntimeError("Group_by aggregators must be a non-empty dict.")

            for agg_label, agg_data in aggregators.items():
                if not isinstance(agg_data, dict):
                    raise RuntimeError(
                        f"Group_by aggregators item: {agg_label} must be a "
                        f"non-empty dict."
                    )

                agg_field = agg_data.get("field", None)
                agg_op = agg_data.get("function", None)

                if agg_field is None and agg_op != "count":
                    raise RuntimeError(
                        f"Group_by: You must include a field to perform {agg_op}"
                    )
                if agg_field is not None and agg_field not in all_valid_fields:
                    raise RuntimeError(
                        f"Group_by aggregators field: {agg_field} is not a valid"
                        " field."
                    )
                if agg_field in group_by_fields:
                    raise RuntimeError(
                        f"Group_by aggregators field: {agg_field} is already "
                        "being grouped upon."
                    )
                if SQLA_FNS.get(agg_op) is None:
                    raise RuntimeError(
                        f"Group_by aggregators fn: {agg_op} is not supported."
                    )

                type_info = (
                    "int"
                    if agg_field is None and agg_op == "count"
                    else dataset_metadata[agg_field]
                )
                if type_info not in SQLA_FNS[agg_op]["types"]:
                    raise RuntimeError(
                        f"Group_by aggregators fn: {agg_op} does not support "
                        f"fields of type: {type_info}"
                    )
                op_type = SQLA_FNS[agg_op]["result_type"]
                agg_type = type_info if op_type == "self" else op_type
                # Add aggregate fields to our dataset metadata so we maintain
                # types of aggregate fields.
                dataset_metadata[agg_label] = agg_type

                available_fields = group_by_fields + list(aggregators.keys())
        else:
            available_fields = all_valid_fields

        having = args.get("having", None)
        if having is not None:
            try:
                having = swc.SQLAWhereExpression.parse_children(having, top_level=True)
            except swc.SqlaWhereParseError as e:
                raise RuntimeError(f"Error parsing having expression: {str(e)}")

        count_fields = args.get("count_fields")
        if count_fields is not None:
            if not isinstance(count_fields, list):
                raise RuntimeError("Count_fields must be a list.")

        if count_fields is not None:
            for field in count_fields:
                if field not in available_fields:
                    raise RuntimeError(
                        f"{field} is not a field in dataset: {dataset_name} or the "
                        "group_by argument."
                    )

        distinct_field = args.get("distinct_field")
        if distinct_field is not None:
            if not isinstance(distinct_field, str):
                raise RuntimeError("distinct_field must be a str.")

            if distinct_field not in available_fields:
                raise RuntimeError(
                    f"{distinct_field} is not a field in dataset: {dataset_name}"
                )

        limit = args.get("limit", None)
        if limit is not None and (
            not isinstance(limit, int) or (isinstance(limit, int) and limit < 1)
        ):
            raise RuntimeError("Limit must be an int > 0")

        offset = args.get("offset", None)
        if offset is not None and (
            not isinstance(offset, int) or (isinstance(offset, int) and offset < 0)
        ):
            raise RuntimeError("Offset must be an int >= 0")

        order_by = args.get("order_by", None)
        if order_by is not None:
            if not isinstance(order_by, list) or len(order_by) < 1:
                raise RuntimeError(
                    "Order_by must be a non-empty list of lists of form: "
                    "[[FIELD_NAME, ASC|DESC]]."
                )
            for o in order_by:
                if not isinstance(o, list) or len(o) != 2:
                    raise RuntimeError("Order By elements must be lists of length 2.")
                field_name, order = o
                if field_name not in available_fields:
                    raise RuntimeError(
                        f"Order_by: {field_name} is not an available field in "
                        f"dataset: {dataset_name} or the group_by argument."
                    )
                elif order.lower() not in ["asc", "desc"]:
                    raise RuntimeError(
                        f"Order_by: {order} must be one of 'asc' or 'desc'"
                    )

        request = args.get("request", None)
        if request is not None:
            try:
                request = swc.SQLAWhereExpression.parse_children(
                    request, top_level=True
                )
            except swc.SqlaWhereParseError as e:
                raise RuntimeError(f"Error parsing request expression: {str(e)}")

        return (
            dataset_name,
            dataset_metadata,
            list(set(available_fields)),
            request,
            limit,
            offset,
            order_by,
            group_by,
            having,
            count_fields,
            distinct_field,
        )
