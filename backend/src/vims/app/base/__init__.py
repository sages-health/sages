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

import logging
import sys

import secure

from cryptography.fernet import MultiFernet
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from vims.core import Config, Dependency, Inject, Reference
from vims.databridge import DataBridgeType
from vims.databridge.sql_alchemy import SqlAlchemyBridge
from vims.databridge.vims import VimsBridge

from ..auth import auth
from ..dashboard import dashboard
from ..database import database
from ..database.models import datasources
from ..dataset import dataset
from ..datasource import datasource
from ..detector import detector
from ..etl import etl
from ..group import group
from ..locale import locale
from ..regionmap import region_map
from ..role import role
from ..settings import Settings
from ..user import user
from ..visualization import visualization


def v1(
    auth: APIRouter = Inject(auth),
    detector: APIRouter = Inject(detector),
    user: APIRouter = Inject(user),
    locale: APIRouter = Inject(locale),
    role: APIRouter = Inject(role),
    group: APIRouter = Inject(group),
    dataset: APIRouter = Inject(dataset),
    datasource: APIRouter = Inject(datasource),
    visualization: APIRouter = Inject(visualization),
    dashboard: APIRouter = Inject(dashboard),
    region_map: APIRouter = Inject(region_map),
    etl: APIRouter = Inject(etl),
):
    router = APIRouter()
    router.include_router(auth, prefix="/auth")
    router.include_router(detector, prefix="/detector")
    router.include_router(user, prefix="/user")
    router.include_router(locale, prefix="/locale")
    router.include_router(role, prefix="/role")
    router.include_router(group, prefix="/group")
    router.include_router(dataset, prefix="/dataset")
    router.include_router(datasource, prefix="/datasource")
    router.include_router(visualization, prefix="/visualization")
    router.include_router(dashboard, prefix="/dashboard")
    router.include_router(region_map, prefix="/map")
    router.include_router(etl, prefix="/etl")
    return router


def api(v1: APIRouter = Inject(v1)):
    router = APIRouter()
    router.include_router(v1, prefix="/v1")
    return router


def base(
    api: APIRouter = Inject(api),
    config=Inject(Config),
):
    if config.get(Settings.ENVIRONMENT) == "production":
        base = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    else:
        base = FastAPI()
    secure_headers = secure.Secure()
    base.include_router(api, prefix="/api")

    @base.middleware("http")
    async def set_secure_headers(request, call_next):
        response = await call_next(request)
        secure_headers.framework.fastapi(response)
        return response

    logging.info(f"RUN MODE: {config.get(Settings.RUN_MODE)}")

    if config.get(Settings.RUN_MODE) == "standalone":
        base.mount("/", StaticFiles(directory="dist", html=True), name="dist")
        logging.info("Running in standalone")

    @base.get("/api/.*", status_code=404, include_in_schema=False)
    def invalid_api():
        return None

    @base.get("/.*", response_class=FileResponse)
    def root():
        return FileResponse("/index.html")

    @base.on_event("startup")
    async def startup():
        fernet = MultiFernet(config.get(Settings.ENCRYPTION_KEYS))

        await database.connect()
        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        query = datasources.select()
        all_datasources = await database.fetch_all(query)
        for ds in all_datasources:
            password = fernet.decrypt(
                bytes(ds.password, sys.getdefaultencoding())
            ).decode(sys.getdefaultencoding())
            if ds.datasource_type == DataBridgeType.SQL_ALCHEMY.value:
                databridge = SqlAlchemyBridge(
                    url=ds.url,
                    password=password,
                    ssl=ds.kwargs["ssl"],
                    min_size=ds.kwargs["min_connection_size"],
                    max_size=ds.kwargs["max_connection_size"],
                )
            else:
                databridge = VimsBridge(
                    url=ds.url, password=password, username=ds.kwargs["username"]
                )
            await databridge.connect()
            databridge_manager.add_databridge(ds.token, databridge)

    @base.on_event("shutdown")
    async def shutdown():
        await database.disconnect()
        databridge_manager = await Dependency.resolve(Reference.DATABRIDGE_MANAGER)
        await databridge_manager.disconnect_all()

    @base.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
        logging.error(f"{request}: {exc_str}")
        content = {"status_code": 10422, "message": exc_str, "data": None}
        return JSONResponse(
            content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    return base
