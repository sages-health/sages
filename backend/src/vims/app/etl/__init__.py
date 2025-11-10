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

# from typing import List

import json
import os

# import aiocsv
import aiofiles

# from Crypto.Cipher import AES
from fastapi import APIRouter, Depends, UploadFile

from vims.app.config import Config

# from vims.app.etl.utils import configuration
# from vims.app.model.etl import MobileData
from vims.app.settings import Settings

from ..auth import require_permission
from ..permissions import Permission
from .ETLJob import ETLJob

# import uuid

# from base64 import b64decode


async def etl():
    router = APIRouter()

    @router.post(
        "/upload",
        response_model=dict,
        dependencies=[Depends(require_permission(Permission.UPLOAD_DATA))],
    )
    async def file_upload(file: UploadFile):
        if not file:
            return {"messages": "No upload file sent"}

        # Create etl-data folder if doesn't exist
        if not os.path.isdir(Config.get(Settings.ETL_DATA_FOLDER)):
            os.mkdir(Config.get(Settings.ETL_DATA_FOLDER))

        async with aiofiles.open(
            Config.get(Settings.ETL_DATA_FOLDER) + "/" + file.filename, "wb"
        ) as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

        return {"Result": "OK"}

    @router.get(
        "/config",
        dependencies=[Depends(require_permission(Permission.UPLOAD_DATA))],
    )
    async def get_configs():
        f = open("./configurations.json")
        return json.load(f)

    @router.post(
        "/dagrun",
        dependencies=[Depends(require_permission(Permission.UPLOAD_DATA))],
    )
    async def dag_run(conf: dict = None):
        """
        :param conf: dict from Request Body. Should be formatted like
        {"conf": {"filetype": <>,
        "filename": <>}}.
        - filetype should correspond to a key  in the
        configurations.json
        - filename will be a file in your etl-data folder, which
        should be a file you uploaded
        via the file_upload endpoint, which places your file in that folder
        :return:
        """
        # Load all configs
        f = open("./configurations.json")
        configs = json.load(f)

        # Pick the config with the key matching the filetype passed
        config = configs[conf["conf"]["filetype"]]
        etl_run = ETLJob(config, conf["conf"]["filename"])

        result = etl_run.execute_etl()
        return {"message": result, "state": result}

    # @router.post(
    #     "/mobile/upload",
    #     dependencies=[Depends(require_permission(Permission.UPLOAD_DATA))],
    # )
    # async def upload_mobile_data(mobile_data: List[MobileData] = None):
    #     key = Config.get(Settings.MOBILE_ETL_ENCRYPTION_KEY).encode()
    #     cipher = AES.new(key, AES.MODE_ECB)
    #     data = {}
    #     for txt_msg in mobile_data:
    #         cipher_text = b64decode(txt_msg.sms_payload.split("|")[1])
    #         # decrypt and remove padding
    #         decrypted = "".join(
    #             c for c in cipher.decrypt(cipher_text).decode() if c.isprintable()
    #         )
    #
    #         file_type = decrypted.split("|")[0]
    #         input_identifier = (
    #             file_type,
    #             txt_msg.phone_number,
    #             txt_msg.date_sent,
    #             txt_msg.date_received,
    #         )
    #         if not data.get(input_identifier):
    #             data[input_identifier] = []
    #
    #         row = {}
    #
    #         for key, value in zip(
    #             decrypted.split("|")[1::2], decrypted.split("|")[2::2]
    #         ):
    #             row[key] = value
    #         data[input_identifier].append(row)
    #         # check that all the keys within each file_type has the same keys
    #         assert data[input_identifier][0].keys() == row.keys()
    #
    #     results = []
    #
    #     for file_to_process, rows in data.items():
    #         # make sure there is data in there to avoid issues later
    #         if not rows[0]:
    #             continue
    #         # get a unique name
    #         file_name_uuid = uuid.uuid4()
    #         # write each file to disk
    #         async with aiofiles.open(
    #             Config.get(Settings.ETL_DATA_FOLDER)
    #             + "/"
    #             + str(file_name_uuid)
    #             + ".csv",
    #             "w",
    #         ) as out_file:
    #             writer = aiocsv.AsyncDictWriter(out_file, fieldnames=rows[0].keys())
    #             await writer.writeheader()
    #             await writer.writerows(rows)
    #
    #         # kick off etl process for each file_to_process
    #         config = configuration[file_to_process[0]]
    #         conf = {
    #             "conf": {
    #                 "file_name": str(file_name_uuid) + ".csv",
    #                 "filetype": file_to_process[0],
    #                 file_to_process[0]: config,
    #
    #         }
    #         etl_run = ETLJob(conf)
    #         # write to logging table
    #         etl_run.write_mobile_log(
    #             input_filename=str(file_name_uuid) + ".csv",
    #             date_sent=file_to_process[2],
    #             date_received=file_to_process[3],
    #             phone_number=file_to_process[1],
    #         )
    #         result = etl_run.execute_etl()
    #         results.append(result)
    #
    #     return results

    return router
