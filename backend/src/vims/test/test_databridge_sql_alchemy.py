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

import datetime
import json
import os
import sys

import pytest

from cryptography.fernet import MultiFernet

from vims.app.config import config
from vims.app.settings import Settings
from vims.core import Dependency
from vims.databridge import DataBridgeType
from vims.databridge.sql_alchemy import SqlAlchemyBridge
from vims.util import cast

pytestmark = pytest.mark.anyio

# TODO-README: Add that the tests are dependent on a specific database at a certain
#  time?
#   * Not the best to have the tests dependent on the content of the db, but if the
#   * data is static it's not the end of the world.


PANET_TOKEN = "aa2458c2-e971-4baf-80df-3b442353508a"
COVID19_TOKEN = "ddd6bd7b-02b6-425f-9024-fe8ba3da094d"
SFPD_INCIDENTS_TOKEN = "5290479b-77bd-4bcc-a6b1-bb25eb5ba726"

PANET_TABLES = {
    "ACDC": {
        "id": "int",
        "raw_file_id": "int",
        "province_state": "str",
        "country_region": "str",
        "lastUpdate": "str",
        "lat": "float",
        "long": "float",
        "confirmed": "float",
        "deaths": "float",
        "fips": "float",
        "incident_rate": "float",
        "total_test_results": "float",
        "case_fatality_ratio": "str",
        "jhu_uid": "float",
        "iso3": "str",
        "testing_rate": "float",
        "date": "str",
        "panet_admin0": "str",
        "panet_admin0_conf": "float",
        "panet_admin1": "str",
        "panet_admin1_conf": "float",
        "panet_admin2": "str",
        "panet_admin2_conf": "float",
        "recovered": "float",
        "active": "float",
        "people_tested": "float",
        "people_hospitalized": "float",
        "mortality_rate": "float",
        "hospitalization_rate": "float",
        "Cases_28_Days": "float",
        "Deaths_28_Days": "float",
        "admin2": "str",
        "combined_key": "str",
    },
    "Mobility": {
        "id": "int",
        "raw_file_id_social": "int",
        "raw_file_id_descartes": "int",
        "date": "str",
        "country_code": "str",
        "admin_level": "int",
        "admin1": "str",
        "admin2": "str",
        "fips": "int",
        "samples": "int",
        "m50": "float",
        "m50_index": "int",
        "DateField": "str",
        "State": "str",
        "Mobility": "float",
        "panet_admin0": "str",
        "panet_admin0_conf": "int",
        "panet_admin1": "str",
        "panet_admin1_conf": "float",
        "panet_admin2": "str",
        "panet_admin2_conf": "float",
    },
    "Omics": {
        "id": "int",
        "raw_file_id": "int",
        "strain": "str",
        "date": "str",
        "gisaid_clade": "str",
        "s1_mutations": "float",
        "clade_membership": "str",
        "country": "str",
        "current_frequency": "float",
        "division": "str",
        "division_exposure": "str",
        "emerging_lineage": "str",
        "genbank_accession": "str",
        "gisaid_epi_isl": "str",
        "host": "str",
        "originating_lab": "str",
        "pango_lineage": "str",
        "recency": "str",
        "region": "str",
        "region_exposure": "str",
        "submitting_lab": "str",
        "author": "str",
        "age": "str",
        "sex": "str",
        "country_exposure": "str",
        "location": "str",
        "logistic_growth": "float",
        "panet_source_path": "str",
        "pangolin_lineage": "str",
        "database": "str",
        "epiweek": "str",
        "variant": "str",
        "pango_lineage_local": "str",
        "category": "str",
        "batch": "str",
        "group": "str",
        "sequencing_date": "str",
        "cluster_id": "str",
        "legacy_clade_membership": "str",
        "subclade_membership": "str",
        "origin_subset": "str",
        "nextstrain_clade": "str",
        "country2": "str",
        "accession_id": "str",
        "submitting_facility": "str",
        "division1": "str",
        "division2": "str",
        "search": "str",
        "ca_lab": "str",
        "county": "str",
        "sequence_processing_date": "str",
        "geoloc_9cat": "str",
        "sequenced_by_2cat": "str",
        "virus": "str",
        "clf_a_exposure": "str",
        "conf_a_exposure": "str",
        "area": "str",
        "update": "str",
        "panet_admin0": "str",
        "panet_admin0_conf": "float",
        "panet_admin1": "str",
        "panet_admin1_conf": "float",
        "panet_admin2": "str",
        "panet_admin2_conf": "float",
    },
    "Policy": {
        "id": "int",
        "raw_file_id": "int",
        "date": "str",
        "policy_text": "str",
        "restrict_close": "int",
        "opening_state": "int",
        "deferring_to_county": "int",
        "testing": "int",
        "education": "int",
        "health_medical": "int",
        "emergency_level": "int",
        "transportation": "int",
        "budget": "int",
        "social_distancing": "int",
        "other": "str",
        "vaccine": "int",
        "admin1": "str",
        "opening_county": "str",
        "panet_admin0": "str",
        "panet_admin0_conf": "float",
        "panet_admin1": "str",
        "panet_admin1_conf": "float",
        "panet_admin2": "str",
        "panet_admin2_conf": "float",
    },
}
COVID19_TABLES = {
    "dailyreports": {
        "date": "datetime",
        "uid": "int",
        "iso2": "str",
        "iso3": "str",
        "code3": "str",
        "fips": "int",
        "admin2": "str",
        "province_state": "str",
        "country_region": "str",
        "last_update": "datetime",
        "lat": "str",
        "long_": "str",
        "confirmed": "float",
        "deaths": "float",
        "recovered": "float",
        "active": "float",
        "combined_key": "str",
        "incident_rate": "float",
        "case_fatality_ratio": "float",
        "population": "int",
    },
}
SFPD_INCIDENTS_TABLES = {
    "incidents": {
        "incident_number": "str",
        "datetime": "datetime",
        "category": "str",
        "description": "str",
        "resolution": "str",
        "pd_district": "str",
        "address": "str",
        "longitude": "float",
        "latitude": "float",
    }
}


@pytest.fixture(scope="session")
async def fernet():
    resolved_config = await Dependency.resolve(config)
    fernet = MultiFernet(resolved_config.get(Settings.ENCRYPTION_KEYS))
    return fernet


@pytest.fixture(scope="session")
async def databridges(fernet):
    databridges = {}
    connection_info = os.environ.get(
        "VIMS_CONNECTION_INFO", "connection-info/connection-info--local.json"
    )
    with open(connection_info, "r") as f:
        for data_bridge_data in json.load(f):
            if data_bridge_data.get("type") == "sql_alchemy":
                encrypted_password = data_bridge_data.get("encrypted_password", None)
                if encrypted_password is not None:
                    password = fernet.decrypt(
                        bytes(encrypted_password, sys.getdefaultencoding())
                    ).decode(sys.getdefaultencoding())
                else:
                    password = ""
                data_bridge = SqlAlchemyBridge(
                    url=data_bridge_data.get("url"),
                    password=password,
                    ssl=data_bridge_data.get("ssl", True),
                    min_size=data_bridge_data.get("min_connection_size", 5),
                    max_size=data_bridge_data.get("max_connection_size", 20),
                    name=data_bridge_data.get("name", ""),
                    display_name=data_bridge_data.get("display_name", ""),
                    datasource_type=DataBridgeType.SQL_ALCHEMY,
                )
                databridges[data_bridge_data.get("token")] = data_bridge

    for token, databridge in databridges.items():
        await databridge.connect()
    yield databridges
    for token, databridge in databridges.items():
        await databridge.disconnect()


@pytest.mark.parametrize(
    "token,gt_dataset_names",
    [
        (PANET_TOKEN, list(PANET_TABLES.keys())),
        (COVID19_TOKEN, list(COVID19_TABLES.keys())),
        (SFPD_INCIDENTS_TOKEN, list(SFPD_INCIDENTS_TABLES.keys())),
    ],
)
async def test_databridge_sql_alchemy__command__list_datasets(
    databridges, token, gt_dataset_names
):
    dataset_name_dicts = await databridges[token].list_datasets()
    assert (
        list(map(lambda x: x["name"], dataset_name_dicts["datasets"]))
        == gt_dataset_names
    )


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata",
    [
        (PANET_TOKEN, "ACDC", PANET_TABLES["ACDC"]),
        (PANET_TOKEN, "Mobility", PANET_TABLES["Mobility"]),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"]),
        (PANET_TOKEN, "Policy", PANET_TABLES["Policy"]),
        (COVID19_TOKEN, "dailyreports", COVID19_TABLES["dailyreports"]),
        (SFPD_INCIDENTS_TOKEN, "incidents", SFPD_INCIDENTS_TABLES["incidents"]),
    ],
)
async def test_databridge_sql_alchemy__command__list_fields(
    databridges, token, dataset_name, dataset_metadata
):
    field_dict = await databridges[token].get_dataset_fields(dataset_name)
    assert field_dict["fields"] == dataset_metadata


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata",
    [
        (PANET_TOKEN, "ACDC", PANET_TABLES["ACDC"]),
        (COVID19_TOKEN, "dailyreports", COVID19_TABLES["dailyreports"]),
        (SFPD_INCIDENTS_TOKEN, "incidents", SFPD_INCIDENTS_TABLES["incidents"]),
    ],
)
async def test_databridge_sql_alchemy__command__query(
    databridges, token, dataset_name, dataset_metadata
):
    query_args = {
        "dataset": {
            "name": dataset_name,
            "fields": dataset_metadata,
        },
        "limit": 1,
    }
    result = await databridges[token].query(query_args)
    assert result.get("values", None) is not None


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,projection",
    [
        (PANET_TOKEN, "ACDC", PANET_TABLES["ACDC"], {"id": 1}),
        (
            PANET_TOKEN,
            "Mobility",
            PANET_TABLES["Mobility"],
            {
                "raw_file_id_social": 1,
                "raw_file_id_descartes": 1,
                "date": 1,
                "Mobility": 1,
            },
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            {"date": 1, "uid": 1, "fips": 1, "province_state": 1, "deaths": 1},
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            {"incident_number": 1, "category": 1, "address": 1, "longitude": 1},
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__projection(
    databridges, token, dataset_name, dataset_metadata, projection
):
    rows_all_fields = await base_query(
        databridges[token], dataset_name, dataset_metadata
    )
    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        projection=projection,
    )

    for row, row_all_fields in zip(rows, rows_all_fields):
        assert len(row) == len(projection)
        for field, val in row.items():
            assert val == row_all_fields[field]


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,limit",
    [
        (PANET_TOKEN, "ACDC", PANET_TABLES["ACDC"], 1),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], 10),
        (PANET_TOKEN, "Policy", PANET_TABLES["Policy"], 100),
        (COVID19_TOKEN, "dailyreports", COVID19_TABLES["dailyreports"], 50),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            200,
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__limit(
    databridges, token, dataset_name, dataset_metadata, limit
):
    rows = await base_query(
        databridges[token], dataset_name, dataset_metadata, limit=limit
    )
    assert len(rows) == limit


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,offset",
    [
        (PANET_TOKEN, "ACDC", PANET_TABLES["ACDC"], 1),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], 10),
        (PANET_TOKEN, "Policy", PANET_TABLES["Policy"], 15),
        (COVID19_TOKEN, "dailyreports", COVID19_TABLES["dailyreports"], 30),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            20,
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__offset(
    databridges, token, dataset_name, dataset_metadata, offset
):
    rows = await base_query(
        databridges[token], dataset_name, dataset_metadata, limit=offset * 2
    )
    offset_rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        limit=offset * 2,
        offset=offset,
    )
    is_offset = True
    for idx, offset_row in enumerate(offset_rows[:offset]):
        is_offset = offset_row == rows[idx + offset]
    assert is_offset


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,order_by",
    [
        (PANET_TOKEN, "ACDC", PANET_TABLES["ACDC"], [("id", "asc")]),
        (
            PANET_TOKEN,
            "Mobility",
            PANET_TABLES["Mobility"],
            [("country_code", "desc")],
        ),
        (
            PANET_TOKEN,
            "Policy",
            PANET_TABLES["Policy"],
            [("panet_admin0_conf", "asc")],
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            [("date", "asc")],
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            [("uid", "desc"), ("date", "asc")],
        ),
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            [("lat", "desc"), ("id", "asc")],
        ),
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            [("combined_key", "asc"), ("lat", "desc"), ("id", "asc")],
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            [("incident_number", "asc")],
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            [("incident_number", "asc"), ("longitude", "desc"), ("datetime", "asc")],
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__order_by(
    databridges, token, dataset_name, dataset_metadata, order_by
):
    projection = {k: 1 for k in map(lambda x: x[0], order_by)}
    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        projection=projection,
        order_by=order_by,
        limit=200,
    )

    is_sorted = True
    last_row = None
    for row in rows:
        if last_row is not None:
            for field, order in order_by:
                if row[field] is not None and last_row[field] is not None:
                    is_sorted = (
                        last_row[field] <= row[field]
                        if order == "asc"
                        else last_row[field] >= row[field]
                    )

        last_row = row

    assert is_sorted


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,grp_field,agg_op,agg_field",
    [
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            "country_region",
            "max",
            "deaths",
        ),
        (
            PANET_TOKEN,
            "Mobility",
            PANET_TABLES["Mobility"],
            "State",
            "max",
            "Mobility",
        ),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], "country", "min", "id"),
        (PANET_TOKEN, "Policy", PANET_TABLES["Policy"], "date", "min", "budget"),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "country_region",
            "max",
            "case_fatality_ratio",
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "province_state",
            "min",
            "uid",
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "country_region",
            "max",
            "date",
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            "pd_district",
            "min",
            "datetime",
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            "pd_district",
            "max",
            "longitude",
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__group_by__max_min(
    databridges,
    token,
    dataset_name,
    dataset_metadata,
    grp_field,
    agg_op,
    agg_field,
):
    agg_label = f"{agg_op}_{agg_field}"
    group_by = {
        "fields": [grp_field],
        "aggregators": {agg_label: {"field": agg_field, "function": agg_op}},
    }

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        limit=1,
        group_by=group_by,
    )
    target = rows[0][grp_field]
    val = rows[0][agg_label]

    if agg_op == "max":
        order_by = [[agg_field, "desc"]]
    elif agg_op == "min":
        order_by = [[agg_field, "asc"]]

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        limit=1,
        order_by=order_by,
        projection={agg_field: 1},
        request={grp_field: {"$eq": target}},
    )
    assert rows[0][agg_field] == val


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,grp_field,agg_op,agg_field",
    [
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            "country_region",
            "sum",
            "deaths",
        ),
        (
            PANET_TOKEN,
            "Mobility",
            PANET_TABLES["Mobility"],
            "State",
            "sum",
            "Mobility",
        ),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], "country", "sum", "id"),
        (PANET_TOKEN, "Policy", PANET_TABLES["Policy"], "date", "sum", "budget"),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "province_state",
            "sum",
            "deaths",
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            "pd_district",
            "sum",
            "longitude",
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__group_by__sum(
    databridges,
    token,
    dataset_name,
    dataset_metadata,
    grp_field,
    agg_op,
    agg_field,
):
    agg_label = f"{agg_op}_{agg_field}"
    group_by = {
        "fields": [grp_field],
        "aggregators": {agg_label: {"field": agg_field, "function": agg_op}},
    }

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        order_by=[[agg_label, "desc"]],
        limit=None,
        group_by=group_by,
    )
    for row in rows:
        # Loop until we get our first not-None value.
        # In the future, this should be handled by a "Having" query.
        if row[agg_label] is not None:
            target = row[grp_field]
            val = cast(row[agg_label], dataset_metadata[agg_field])
            break

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        limit=None,
        projection={agg_field: 1},
        request={grp_field: {"$eq": target}},
    )
    total = 0
    for row in rows:
        if row[agg_field] is not None:
            total += cast(row[agg_field], dataset_metadata[agg_field])

    assert total == val


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,grp_field,agg_op,agg_field",
    [
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            ["country_region", "province_state"],
            "count",
            "deaths",
        ),
        (
            PANET_TOKEN,
            "Mobility",
            PANET_TABLES["Mobility"],
            ["country_code", "State"],
            "count",
            "Mobility",
        ),
        (
            PANET_TOKEN,
            "Omics",
            PANET_TABLES["Omics"],
            ["country", "region"],
            "count",
            "id",
        ),
        (
            PANET_TOKEN,
            "Policy",
            PANET_TABLES["Policy"],
            ["opening_county", "date"],
            "count",
            "budget",
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            ["pd_district", "category"],
            "count",
            "incident_number",
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__group_by__count(
    databridges,
    token,
    dataset_name,
    dataset_metadata,
    grp_field,
    agg_op,
    agg_field,
):
    agg_label = f"{agg_op}_{agg_field}"
    group_by = {
        "fields": grp_field,
        "aggregators": {agg_label: {"field": agg_field, "function": agg_op}},
    }

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        order_by=[[agg_label, "desc"]],
        limit=1,
        group_by=group_by,
    )

    target0 = rows[0][grp_field[0]]
    target1 = rows[0][grp_field[1]]
    val = rows[0][agg_label]

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        limit=None,
        projection={agg_field: 1},
        request={
            "$and": [
                {grp_field[0]: {"$eq": target0}},
                {grp_field[1]: {"$eq": target1}},
                {agg_field: {"$isnot": None}},
            ]
        },
    )
    assert len(rows) == val


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,grp_field,agg_op",
    [
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            ["country_region", "province_state"],
            "count",
        ),
        (
            PANET_TOKEN,
            "Mobility",
            PANET_TABLES["Mobility"],
            ["country_code", "State"],
            "count",
        ),
        (
            PANET_TOKEN,
            "Omics",
            PANET_TABLES["Omics"],
            ["country", "region"],
            "count",
        ),
        (
            PANET_TOKEN,
            "Policy",
            PANET_TABLES["Policy"],
            ["opening_county", "date"],
            "count",
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            ["pd_district", "category"],
            "count",
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__group_by__count__no_field(
    databridges,
    token,
    dataset_name,
    dataset_metadata,
    grp_field,
    agg_op,
):
    agg_label = f"{agg_op}__no_field"
    group_by = {
        "fields": grp_field,
        "aggregators": {agg_label: {"function": agg_op}},
    }

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        order_by=[[agg_label, "desc"]],
        limit=1,
        group_by=group_by,
    )

    target0 = rows[0][grp_field[0]]
    target1 = rows[0][grp_field[1]]
    val = rows[0][agg_label]

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        limit=None,
        request={
            "$and": [
                {grp_field[0]: {"$eq": target0}},
                {grp_field[1]: {"$eq": target1}},
            ]
        },
    )
    assert len(rows) == val


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,grp_fields,aggregators",
    [
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            ["country_region", "province_state"],
            {
                "max_deaths": {"field": "deaths", "function": "max"},
                "total_deaths": {"field": "deaths", "function": "sum"},
            },
        ),
        (
            PANET_TOKEN,
            "Mobility",
            PANET_TABLES["Mobility"],
            ["country_code", "State"],
            {
                "min_samples": {"field": "samples", "function": "min"},
                "max_Mobility": {"field": "Mobility", "function": "max"},
            },
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            ["country_region", "province_state"],
            {
                "total_deaths": {"field": "deaths", "function": "sum"},
                "total_population": {"field": "population", "function": "sum"},
            },
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            ["country_region", "date"],
            {
                "total_deaths": {"field": "deaths", "function": "sum"},
                "max_deaths": {"field": "deaths", "function": "max"},
            },
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            ["pd_district", "category"],
            {
                "count_incident_numbers": {
                    "field": "incident_number",
                    "function": "count",
                },
                "max_datetime": {"field": "datetime", "function": "max"},
            },
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__group_by__complex(
    databridges,
    token,
    dataset_name,
    dataset_metadata,
    grp_fields,
    aggregators,
):
    group_by = {
        "fields": grp_fields,
        "aggregators": aggregators,
    }
    agg_labels = list(aggregators.keys())
    agg_fields = []
    agg_fns = []
    for agg_label, agg_data in aggregators.items():
        agg_fields.append(agg_data["field"])
        agg_fns.append(agg_data["function"])

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        order_by=[[agg_labels[0], "desc"]],
        limit=None,
        group_by=group_by,
    )
    for row in rows:
        # Get the first non-None aggregated vals.
        if row[agg_labels[0]] is not None and row[agg_labels[1]] is not None:
            target_0 = row[grp_fields[0]]
            target_1 = row[grp_fields[1]]
            vals_0 = row[agg_labels[0]]
            vals_1 = row[agg_labels[1]]
            break

    computed_vals_0 = None
    computed_vals_1 = None
    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        limit=None,
        projection={
            grp_fields[0]: 1,
            grp_fields[1]: 1,
            agg_fields[0]: 1,
            agg_fields[1]: 1,
        },
        request={
            "$and": [
                {grp_fields[0]: {"$eq": target_0}},
                {grp_fields[1]: {"$eq": target_1}},
                {agg_fields[0]: {"$isnot": None}},
                {agg_fields[1]: {"$isnot": None}},
            ]
        },
    )

    for row in rows:
        val_0 = row[agg_fields[0]]
        val_1 = row[agg_fields[1]]

        if agg_fns[0] == "max":
            if computed_vals_0 is None or val_0 > computed_vals_0:
                computed_vals_0 = val_0
        elif agg_fns[0] == "sum":
            if computed_vals_0 is None:
                computed_vals_0 = 0
            computed_vals_0 += val_0
        elif agg_fns[0] == "min":
            if computed_vals_0 is None or val_0 < computed_vals_0:
                computed_vals_0 = val_0
        elif agg_fns[0] == "count":
            if computed_vals_0 is None:
                computed_vals_0 = 0
            computed_vals_0 += 1

        if agg_fns[1] == "max":
            if computed_vals_1 is None or val_1 > computed_vals_1:
                computed_vals_1 = val_1
        elif agg_fns[1] == "sum":
            if computed_vals_1 is None:
                computed_vals_1 = 0
            computed_vals_1 += val_1
        elif agg_fns[1] == "min":
            if computed_vals_1 is None or val_1 < computed_vals_1:
                computed_vals_1 = val_1
        elif agg_fns[1] == "count":
            if computed_vals_1 is None:
                computed_vals_1 = 0
            computed_vals_1 += 1

    assert vals_0 == computed_vals_0 and vals_1 == computed_vals_1


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,grp_field,aggregator,op,val",
    [
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            "country_region",
            {"max_deaths": {"field": "deaths", "function": "max"}},
            "gt",
            5000,
        ),
        (
            PANET_TOKEN,
            "Mobility",
            PANET_TABLES["Mobility"],
            "State",
            {"min_Mobility": {"field": "Mobility", "function": "min"}},
            "lt",
            20.0,
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "country_region",
            {"min_date": {"field": "date", "function": "min"}},
            "lt",
            datetime.datetime(2022, 1, 1),
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            "pd_district",
            {"min_datetime": {"field": "datetime", "function": "min"}},
            "gt",
            datetime.datetime(2014, 1, 1),
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__having(
    databridges,
    token,
    dataset_name,
    dataset_metadata,
    grp_field,
    aggregator,
    op,
    val,
):
    group_by = {
        "fields": [grp_field],
        "aggregators": aggregator,
    }
    agg_label = list(aggregator.keys())[0]
    agg_field = aggregator[agg_label]["field"]
    order_by = [[f"{agg_label}", "asc" if op.startswith("g") else "desc"]]

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        limit=None,
        group_by=group_by,
        order_by=order_by,
        having={f"{agg_label}": {f"${op}": val}},
    )

    field_type = dataset_metadata[agg_field]
    for r in rows:
        if op == "gt":
            assert cast(r[agg_label], field_type) > val
        elif op == "ge":
            assert cast(r[agg_label], field_type) >= val
        elif op == "lt":
            assert cast(r[agg_label], field_type) < val
        elif op == "le":
            assert cast(r[agg_label], field_type) <= val
        elif op == "eq":
            assert cast(r[agg_label], field_type) == val


async def test_databridge_sql_alchemy__command__query__having__and__1(
    databridges,
):
    token = COVID19_TOKEN
    dataset_name = "dailyreports"
    dataset_metadata = COVID19_TABLES["dailyreports"]
    group_by = {
        "fields": ["country_region"],
        "aggregators": {
            "min_date": {"field": "date", "function": "min"},
            "total_deaths": {"field": "deaths", "function": "sum"},
            "max_deaths": {"field": "deaths", "function": "max"},
        },
    }
    having = {
        "$and": [
            {"min_date": {"$ge": datetime.datetime(2022, 1, 1)}},
            {"total_deaths": {"$lt": 10000}},
            {"max_deaths": {"$gt": 500}},
        ]
    }

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        limit=None,
        group_by=group_by,
        having=having,
    )

    for r in rows:
        assert r["min_date"] >= datetime.datetime(2022, 1, 1)
        assert r["total_deaths"] < 10000
        assert r["max_deaths"] > 500


async def test_databridge_sql_alchemy__command__query__having__or__1(
    databridges,
):
    token = PANET_TOKEN
    dataset_name = "Mobility"
    dataset_metadata = PANET_TABLES["Mobility"]
    group_by = {
        "fields": ["country_code", "State"],
        "aggregators": {
            "min_Mobility": {"field": "Mobility", "function": "min"},
            "max_Mobility": {"field": "Mobility", "function": "max"},
        },
    }
    having = {
        "$or": [
            {"min_Mobility": {"$ge": 60.0}},
            {"max_Mobility": {"$le": 5.0}},
        ]
    }

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        limit=None,
        group_by=group_by,
        having=having,
    )

    for r in rows:
        assert r["min_Mobility"] >= 60.0
        assert r["max_Mobility"] <= 5.0


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,field,op,val",
    [
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "date",
            "gt",
            datetime.datetime(2021, 1, 1),
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "date",
            "ge",
            datetime.datetime(2021, 1, 1),
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "date",
            "lt",
            datetime.datetime(2021, 1, 1),
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "date",
            "le",
            datetime.datetime(2021, 1, 1),
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "date",
            "eq",
            datetime.datetime(2021, 1, 1),
        ),
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            "country_region",
            "gt",
            "South Korea",
        ),
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            "country_region",
            "ge",
            "South Korea",
        ),
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            "country_region",
            "lt",
            "South Korea",
        ),
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            "country_region",
            "le",
            "South Korea",
        ),
        (
            PANET_TOKEN,
            "ACDC",
            PANET_TABLES["ACDC"],
            "country_region",
            "eq",
            "South Korea",
        ),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], "s1_mutations", "gt", 7),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], "s1_mutations", "ge", 7),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], "s1_mutations", "lt", 7),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], "s1_mutations", "le", 7),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], "s1_mutations", "eq", 7),
        (
            PANET_TOKEN,
            "Omics",
            PANET_TABLES["Omics"],
            "panet_admin0_conf",
            "gt",
            0.3,
        ),
        (
            PANET_TOKEN,
            "Omics",
            PANET_TABLES["Omics"],
            "panet_admin0_conf",
            "ge",
            0.333333333,
        ),
        (
            PANET_TOKEN,
            "Omics",
            PANET_TABLES["Omics"],
            "panet_admin0_conf",
            "lt",
            0.4,
        ),
        (
            PANET_TOKEN,
            "Omics",
            PANET_TABLES["Omics"],
            "panet_admin0_conf",
            "le",
            7,
        ),
        (
            PANET_TOKEN,
            "Omics",
            PANET_TABLES["Omics"],
            "panet_admin0_conf",
            "eq",
            0.333333333,
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            "pd_district",
            "eq",
            "BAYVIEW",
        ),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            "address",
            "eq",
            "800 Block of BRYANT ST",
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__conditional__ordering_ops(
    databridges, token, dataset_name, dataset_metadata, field, op, val
):
    order_by = [[f"{field}", "asc" if op.startswith("g") else "desc"]]
    request = {f"{field}": {f"${op}": val}}
    projection = {k: 1 for k in map(lambda x: x[0], order_by)}

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        projection=projection,
        request=request,
        order_by=order_by,
        limit=250,
    )
    field_type = dataset_metadata[field]
    for r in rows:
        if op == "gt":
            assert cast(r[field], field_type) > val
        elif op == "ge":
            assert cast(r[field], field_type) >= val
        elif op == "lt":
            assert cast(r[field], field_type) < val
        elif op == "le":
            assert cast(r[field], field_type) <= val
        elif op == "eq":
            assert cast(r[field], field_type) == val

    assert True


@pytest.mark.parametrize(
    "op,arg",
    [
        ("eq", "Maryland"),
        ("like", "%arylan%"),
        ("ilike", "%ArYlaN%"),
        ("notlike", "%arylan%"),
        ("notilike", "%ArYlaN%"),
        ("startswith", "mary"),
        ("endswith", "land"),
        ("contains", "ryla"),
    ],
)
async def test_databridge_sql_alchemy__command__query__conditional__str_ops(
    databridges, op, arg
):
    token = COVID19_TOKEN
    dataset_name = "dailyreports"
    dataset_metadata = COVID19_TABLES["dailyreports"]
    request = {"province_state": {f"${op}": arg}}
    projection = {"province_state": 1}

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        projection=projection,
        request=request,
        limit=100,
    )
    for r in rows:
        if op in ["like", "contains"]:
            assert arg[1:-1] in r["province_state"]
        elif op == "eq":
            assert r["province_state"] == arg
        elif op == "ilike":
            assert arg[1:-1].lower() in r["province_state"].lower()
        elif op in "notlike":
            assert arg[1:-1] not in r["province_state"]
        elif op in "notilike":
            assert arg[1:-1].lower() not in r["province_state"].lower()
        elif op == "startswith":
            assert r["province_state"].startswith(arg)
        elif op == "endswith":
            assert r["province_state"].endswith(arg)

    assert True


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,field,op",
    [
        (PANET_TOKEN, "ACDC", PANET_TABLES["ACDC"], "province_state", "is"),
        (PANET_TOKEN, "ACDC", PANET_TABLES["ACDC"], "province_state", "isnot"),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], "current_frequency", "is"),
        (
            PANET_TOKEN,
            "Omics",
            PANET_TABLES["Omics"],
            "current_frequency",
            "isnot",
        ),
        (PANET_TOKEN, "Policy", PANET_TABLES["Policy"], "panet_admin2", "is"),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "uid",
            "is",
        ),
        (
            COVID19_TOKEN,
            "dailyreports",
            COVID19_TABLES["dailyreports"],
            "uid",
            "isnot",
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__conditional__is_ops(
    databridges, token, dataset_name, dataset_metadata, field, op
):
    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        request={f"{field}": {f"${op}": None}},
        projection={field: 1},
        limit=200,
    )

    for r in rows:
        if op == "is":
            assert r[field] is None
        else:
            assert r[field] is not None


async def test_databridge_sql_alchemy__command__query__conditional__logical_and__1(
    databridges,
):
    token = COVID19_TOKEN
    dataset_name = "dailyreports"
    dataset_metadata = COVID19_TABLES["dailyreports"]
    request = {
        "$and": [
            {"province_state": {"$contains": "arylan"}},
            {"confirmed": {"$gt": 20}},
        ]
    }

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        projection={"province_state": 1, "confirmed": 1},
        request=request,
        limit=1000,
    )
    for r in rows:
        assert (
            "arylan" in r["province_state"]
            and cast(r["confirmed"], dataset_metadata["confirmed"]) > 20
        )

    assert True


async def test_databridge_sql_alchemy__command__query__conditional__logical_or__1(
    databridges,
):
    token = COVID19_TOKEN
    dataset_name = "dailyreports"
    dataset_metadata = COVID19_TABLES["dailyreports"]
    request = {
        "$or": [{"province_state": {"$contains": "arylan"}}, {"confirmed": {"$gt": 20}}]
    }

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        projection={"province_state": 1, "confirmed": 1},
        request=request,
        limit=1000,
    )
    for r in rows:
        assert (
            "arylan" in r["province_state"]
            or cast(r["confirmed"], dataset_metadata["confirmed"]) > 20
        )

    assert True


async def test_databridge_sql_alchemy__command__query__conditional__logical_not__1(
    databridges,
):
    token = COVID19_TOKEN
    dataset_name = "dailyreports"
    dataset_metadata = COVID19_TABLES["dailyreports"]
    request = {
        "$not": {
            "$or": [
                {"province_state": {"$contains": "arylan"}},
                {"confirmed": {"$gt": 20}},
            ]
        }
    }

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        projection={"province_state": 1, "confirmed": 1},
        request=request,
        limit=1000,
    )
    for r in rows:
        assert (
            "arylan" not in r["province_state"]
            and cast(r["confirmed"], dataset_metadata["confirmed"]) <= 20
        )

    assert True


async def test_databridge_sql_alchemy__command__query__conditional__logical_complex__1(
    databridges,
):
    token = COVID19_TOKEN
    dataset_name = "dailyreports"
    dataset_metadata = COVID19_TABLES["dailyreports"]
    request = {
        "$or": [
            {
                "$not": {
                    "$or": [
                        {"province_state": {"$contains": "arylan"}},
                        {"confirmed": {"$gt": 20}},
                    ]
                }
            },
            {"country_region": {"$eq": "Canada"}},
        ]
    }

    rows = await base_query(
        databridges[token],
        dataset_name,
        dataset_metadata,
        projection={"province_state": 1, "confirmed": 1, "country_region": 1},
        request=request,
        limit=10000,
    )
    for r in rows:
        assert (
            "arylan" not in r["province_state"]
            and cast(r["confirmed"], dataset_metadata["confirmed"]) <= 20
        ) or (r["country_region"] == "Canada")

    assert True


@pytest.mark.parametrize(
    "token,dataset_name,dataset_metadata,field",
    [
        (PANET_TOKEN, "ACDC", PANET_TABLES["ACDC"], "date"),
        (PANET_TOKEN, "Mobility", PANET_TABLES["Mobility"], "date"),
        (PANET_TOKEN, "Omics", PANET_TABLES["Omics"], "date"),
        (PANET_TOKEN, "Policy", PANET_TABLES["Policy"], "date"),
        (COVID19_TOKEN, "dailyreports", COVID19_TABLES["dailyreports"], "date"),
        (
            SFPD_INCIDENTS_TOKEN,
            "incidents",
            SFPD_INCIDENTS_TABLES["incidents"],
            "datetime",
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__count__distinct(
    databridges, token, dataset_name, dataset_metadata, field
):
    request = {
        "count_fields": [
            field,
        ]
    }

    rows = await base_query(
        databridges[token], dataset_name, dataset_metadata, **request
    )

    for row in rows:
        assert type(row[f"count_distinct_{field}"]) is int


@pytest.mark.parametrize(
    "query_args,error",
    [
        ({}, "No dataset info provided"),
        ({"dataset": None}, "No dataset info provided"),
        ({"dataset": {}}, "No dataset name provided"),
        ({"dataset": {"name": None}}, "No dataset name provided"),
        (
            {"dataset": {"name": "test", "fields": None}},
            "No dataset fields provided",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": ["field1", "field2"],
                }
            },
            "Dataset fields must be a non-empty dict.",
        ),
        (
            {"dataset": {"name": "test", "fields": {}}},
            "Dataset fields must be a non-empty dict.",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "projection": ["test"],
            },
            "Projection must be a dict.",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "projection": {"test": 1},
            },
            "test is not a field in dataset: test.",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "limit": "test",
            },
            "Limit must be an int > 0",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "limit": 1.0,
            },
            "Limit must be an int > 0",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "limit": -1,
            },
            "Limit must be an int > 0",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "offset": "test",
            },
            "Offset must be an int >= 0",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "offset": 1.0,
            },
            "Offset must be an int >= 0",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "offset": -1,
            },
            "Offset must be an int >= 0",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "order_by": {},
            },
            "Order_by must be a non-empty list of lists of form: "
            "[[FIELD_NAME, ASC|DESC]].",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "order_by": [],
            },
            "Order_by must be a non-empty list of lists of form: "
            "[[FIELD_NAME, ASC|DESC]].",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "order_by": [[1]],
            },
            "Order By elements must be lists of length 2.",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "order_by": [["test", "test"]],
            },
            "Order_by: test is not an available field in dataset: test or the "
            "group_by argument.",
        ),
        (
            {
                "dataset": {
                    "name": "test",
                    "fields": PANET_TABLES["ACDC"],
                },
                "order_by": [["deaths", "test"]],
            },
            "Order_by: test must be one of 'asc' or 'desc'",
        ),
    ],
)
async def test_databridge_sql_alchemy__command__query__malformed(
    databridges, query_args, error
):
    result = await databridges[PANET_TOKEN].query(query_args)
    assert result["error"] == error


async def base_query(
    databridge,
    dataset_name,
    dataset_metadata,
    projection=None,
    request=None,
    limit=10,
    offset=None,
    order_by=None,
    group_by=None,
    having=None,
    transformations=None,
    count_fields=None,
    distinct_field=None,
):
    query_args = {
        "dataset": {
            "name": dataset_name,
            "fields": dataset_metadata,
        },
        "format": None,
        "projection": projection,
        "request": request,
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "group_by": group_by,
        "having": having,
        "transformations": transformations,
        "count_fields": count_fields,
        "distinct_field": distinct_field,
    }
    results = await databridge.query(query_args)
    print(results)
    return results["values"]
