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

from typing import Any, Dict

import datetime

import httpx

from vims.core import getLogger
from vims.databridge import DataBridge

log = getLogger(__name__)


class VimsBridge(DataBridge):
    def __init__(self, url="", username="", password="", **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.username = username
        self.password = password
        self.access_token = None
        self.access_token_expiration = None

    async def connect(self):
        if (
            self.access_token is None
            or datetime.datetime.now() >= self.access_token_expiration
        ):
            async with httpx.AsyncClient() as client:
                headers = {
                    "Accept": "application/json",
                }
                body = {"username": self.username, "password": self.password}
                try:
                    r = await client.post(
                        f"{self.url}/auth/login", headers=headers, data=body
                    )
                    r_json = r.json()
                    if r_json.get("access_token") is not None:
                        self.access_token = r_json["access_token"]
                        self.access_token_expiration = datetime.datetime.fromisoformat(
                            r_json["expires"]
                        )
                    else:
                        log.error(f"No access token in response from: {self.url}")
                except httpx.ConnectError:
                    log.error(f"Failed to connect to: {self.url}")
                except httpx.ReadTimeout:
                    log.error(f"Read Timeout while trying to connect to: {self.url}")

    async def disconnect(self):
        if (
            self.access_token is not None
            and datetime.datetime.now() < self.access_token_expiration
        ):
            async with httpx.AsyncClient() as client:
                headers = {
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.access_token}",
                }
                try:
                    await client.get(f"{self.url}/auth/logout", headers=headers)
                except httpx.ConnectError:
                    log.error(f"Failed to connect to: {self.url}")
                except httpx.ReadTimeout:
                    log.error(f"Read Timeout while trying to connect to: {self.url}")

        self.access_token = None
        self.access_token_expiration = None

    async def ping(self):
        await self.connect()
        async with httpx.AsyncClient() as client:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }
            try:
                r = await client.get(f"{self.url}/auth/ping", headers=headers)
                return r.json()
            except httpx.ConnectError:
                log.error(f"Failed to connect to: {self.url}")
            except httpx.ReadTimeout:
                log.error(f"Read Timeout while trying to connect to: {self.url}")
        return False

    async def list_datasets(self):
        # Reach out to remote instance and get all datasets that the remote user has
        # access to.
        await self.connect()
        async with httpx.AsyncClient() as client:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }
            params = {
                "limit": 999999,  # just put in some maximum limit so we get them all.
            }
            error = None
            try:
                r = await client.get(
                    f"{self.url}/dataset", headers=headers, params=params
                )
                datasets = []
                for dataset in r.json():
                    datasets.append(
                        {"name": dataset["id"], "display_name": dataset["display_name"]}
                    )
                return {"datasets": datasets, "error": error}
            except httpx.ConnectError:
                error = f"Failed to connect to: {self.url}"
                log.error(error)
            except httpx.ReadTimeout:
                error = f"Read Timeout while trying to connect to: {self.url}"
                log.error(error)
        return {"datasets": [], "error": error}

    async def get_dataset_fields(self, dataset_name: str):
        await self.connect()
        async with httpx.AsyncClient() as client:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }
            error = None
            try:
                r = await client.get(
                    f"{self.url}/dataset/{dataset_name}", headers=headers
                )
                fields = {}
                for field in r.json()["fields"]:
                    fields[field["data_field_name"]] = field["data_field_type"]
                return {"fields": fields, "error": error}
            except httpx.ConnectError:
                error = f"Failed to connect to: {self.url}"
                log.error(error)
            except httpx.ReadTimeout:
                error = f"Read Timeout while trying to connect to: {self.url}"
                log.error(error)
        return {"fields": [], "error": error}

    async def get_dataset_field_values(self, dataset_name: str, field_name: str):
        await self.connect()
        async with httpx.AsyncClient() as client:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }
            error = None
            try:
                r = await client.get(
                    f"{self.url}/dataset/{dataset_name}/{field_name}/values",
                    headers=headers,
                )
                values = []
                for value in r.json()["values"]:
                    values.append(value[field_name])
                return {"values": values, "error": error}
            except httpx.ConnectError:
                error = f"Failed to connect to: {self.url}"
                log.error(error)
            except httpx.ReadTimeout:
                error = f"Read Timeout while trying to connect to: {self.url}"
                log.error(error)
        return {"values": [], "error": error}

    async def query(self, query_args: Dict[str, Any]):
        await self.connect()
        async with httpx.AsyncClient() as client:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }

            query = {
                "computed": query_args["computed"],
                "request": query_args["request"],
                "projection": query_args["projection"],
                "group_by": query_args["group_by"],
                "limit": query_args["limit"],
                "offset": query_args["offset"],
                "order_by": query_args["order_by"],
                "transformations": query_args["transformations"],
                "count_fields": query_args["count_fields"],
                "distinct_field": query_args["distinct_field"],
            }

            try:
                r = await client.post(
                    f'{self.url}/dataset/{query_args["dataset"]["name"]}/query',
                    headers=headers,
                    json=query,
                    timeout=50,
                )
                r_json = r.json()
                return r_json[0]
            except httpx.ConnectError:
                error = f"Failed to connect to: {self.url}"
                log.error(error)
            except httpx.ReadTimeout:
                error = f"Read Timeout while trying to connect to: {self.url}"
                log.error(error)

        return {"values": [], "total": -1, "error": error}
