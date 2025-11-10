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

import asyncio
import multiprocessing
import sys

from argparse import ArgumentParser
from asyncio import AbstractEventLoop

from fastapi import FastAPI
from uvicorn.config import Config as UvicornConfig
from uvicorn.server import Server

from vims.app.base import base
from vims.app.config import config
from vims.app.settings import Settings
from vims.core import Config, Dependency, Inject, Reference, getLogger, logging_init

log = getLogger(__name__)


class DataBridgeManager:
    def __init__(self):
        self.databridges = {}

    def add_databridge(self, token, databridge):
        self.databridges[token] = databridge

    def get_databridge(self, token):
        return self.databridges.get(token, None)

    async def disconnect_all(self):
        for token, databridge in self.databridges.items():
            await databridge.disconnect()


def server_config(base: FastAPI = Inject(base), config: Config = Inject(config)):
    port = config.get(Settings.PORT)
    host = config.get(Settings.HOST)
    log.info(f"Local: http://localhost:{port}")
    multiprocessing.freeze_support()
    return UvicornConfig(
        base,
        host=host,
        port=port,
        log_config=None,
    )


def server(config: UvicornConfig = Inject(server_config)):
    return Server(config)


async def main(loop: AbstractEventLoop, *args):
    def loop_factory():
        return loop

    def args_factory():
        parser = ArgumentParser(prog="python -m vims.app")
        return parser.parse_args(args)

    def get_databridge_manager():
        databridge_manager = DataBridgeManager()
        return databridge_manager

    Dependency.register(Reference.LOOP, loop_factory)
    Dependency.register(Reference.ARGS, args_factory)
    Dependency.register(Reference.DATABRIDGE_MANAGER, get_databridge_manager)

    main: Server = await Dependency.resolve(server)
    await main.serve()


def run(*args):
    if len(args) == 0:
        args = sys.argv[1:]
    logging_init()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop, *args))


run()
