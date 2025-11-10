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

import functools
import traceback

import numpy as np
import pandas as pd
import polars as pl

from sqlalchemy import create_engine, insert, inspect, text
from sqlalchemy.exc import NoSuchTableError

import vims.app.etl.models as models
import vims.app.etl.utils as utils

from vims.app.config import Config
from vims.app.settings import Settings


class ETLJob:
    etl_df = None
    conf = None
    engine = None
    source_directory = None
    VIMS_PRIMARY_KEY = None
    DB_CONNECTION_STRING = None
    task_process = None
    temp_table_name = None

    def __init__(self, config: dict, file_name: str):
        self.conf = config
        self.file_name = file_name
        self.source_directory = Config.get(Settings.ETL_DATA_FOLDER)
        self.VIMS_PRIMARY_KEY = Config.get(Settings.ETL_PRIMARY_KEY_COLUMN_NAME)
        self.DB_CONNECTION_STRING = Config.get(Settings.ETL_CONNECTION_URL)
        self.engine = create_engine(self.DB_CONNECTION_STRING)

        self.use_temp_table = False

        self.task_process = [
            self.create_table,
            self.read_df,
            self.rename_columns,
            self.replace_values,
            self.convert_dates,
            self.cast_columns,
            self.additional_transformations,
            self.create_primary_key,
            self.dedupe_insert,
        ]

    def write_mobile_log(
        self, input_filename: str, date_sent: str, date_received: str, phone_number: str
    ):
        con = self.engine.connect()
        if not inspect(self.engine).has_table(models.mobile_logging_table):
            models.mobile_logging_table.create(con)

        stmt = insert(models.mobile_logging_table).values(
            input_filename=input_filename,
            date_sent=date_sent,
            date_received=date_received,
            phone_number=phone_number,
        )
        con.execute(stmt)

    def execute_etl(self):
        try:
            for func in self.task_process:
                func()
            return "success"
        except Exception:
            print(traceback.format_exc())
            return "failed"
        finally:
            # If things go right, this shouldn't be necessary, but in case a step
            # fails before the end of the process, have a cleanup script to
            # remove the _temp table
            try:
                if self.temp_table_name:
                    con = self.engine.connect()
                    con.execute(text(f"drop table if exists {self.temp_table_name}"))
            except Exception:
                print(traceback.format_exc())
                pass

    def create_table(self) -> None:
        table_name = self.conf["table"]["name"]
        new_table_definition = self.conf["table"]

        self.temp_table_name = f"{table_name}_temp"
        con = self.engine.connect()

        # use an inspect to find the current state of this table in the DB
        insp = inspect(self.engine)
        # try/catch here is to handle if this table has never been created
        try:
            old_column_names = [f'{i["name"]}' for i in insp.get_columns(table_name)]
        except NoSuchTableError:
            # if old table doesn't exist, make it, without temp in the name
            new_table = utils.build_table_from_dict(self.conf["table"])
            new_table.create(con)
            old_column_names = [f'{i["name"]}' for i in insp.get_columns(table_name)]

        # create the temp table to include all the columns from the existing table
        con.execute(
            text(
                f"CREATE TABLE {self.temp_table_name} AS SELECT * FROM {table_name}"
                f" WHERE 0"
            )
        )

        # column names need to be quoted for the postgres syntax for some awful reason
        old_column_names_with_quotes = [f'"{i}"' for i in old_column_names]

        # find all the NEW columns in the input config and add them to the temp table
        for column, data_type in new_table_definition["columns"].items():
            if column not in old_column_names:
                sql_column_type = utils.json_input_sql_types_as_strings[data_type]
                con.execute(
                    f"alter table {self.temp_table_name} add {column} {sql_column_type}"
                )
                # if at least 1 new column is added, use the temp table in later steps
                self.use_temp_table = True

        # if we made a new table, populate it with the old data
        if self.use_temp_table:
            # take the data from the old table and put it in the new tab;e
            con.execute(
                text(
                    f"insert into {self.temp_table_name} ("
                    f"{', '.join(old_column_names_with_quotes)}) select "
                    f"{', '.join(old_column_names_with_quotes)} from {table_name}"
                )
            )

    def read_df(self) -> None:
        """Reads an input file into a dataframe using the specified reader function
        and arguments"""

        reader = self.conf["reader"]
        reader = utils.readers[reader]
        reader_arguments = self.conf["reader_arguments"]
        df = reader(self.source_directory + "/" + self.file_name, **reader_arguments)
        df = df.update(df.select(pl.col(pl.Utf8).str.strip_chars()))

        self.etl_df = df

    def rename_columns(self) -> None:
        """Rename columns to remove unwanted characters that don't mesh well with SQL
        tables using regular expressions.  If no replacement configuration is given,
        a default will be used.

        In addition, an optional renaming callable can be passed in with kwargs that
        will also be applied.
        """

        # if no column_name_replacements are specifed, use the default set in utils
        column_name_replacement = utils.column_name_replacements[
            self.conf.get(
                "column_name_replacements", utils.DEFAULT_COLUMN_NAME_REPLACEMENTS
            )
        ]

        func_name = self.conf.get("column_rename_func", {}).get("function", None)
        func_args = self.conf.get("column_rename_func", {}).get("func_args", None)

        self.etl_df.columns = [
            functools.reduce(
                lambda name, item: item[0].sub(item[1], name),
                column_name_replacement.items(),
                col,
            )
            for col in self.etl_df.columns
        ]

        if callable(utils.col_rename_funcs.get(func_name)) and func_args:
            self.etl_df = utils.col_rename_funcs.get(func_name)(
                self.etl_df, **func_args
            )

    def replace_values(self) -> None:
        """Replace certain un-wanted values in a dataframe with other values.
        For example, replacing the string 'N/A' with None.

        If no configuration is passed in, a default one will be used.
        """
        cell_value_replacements = self.conf.get(
            "cell_value_replacements", utils.DEFAULT_CELL_VALUE_REPLACEMENTS_NAMES
        )

        for cell_value_replacement in cell_value_replacements:
            self.etl_df = self.etl_df.with_columns(
                pl.when(
                    pl.col(pl.Utf8).str.contains(
                        utils.cell_replacements[cell_value_replacement][0]
                    )
                )
                .then(utils.cell_replacements[cell_value_replacement][1])
                .otherwise(pl.col(pl.Utf8))  # keep original value
                .name.keep()
            )

    def convert_dates(self) -> None:
        """Convert date fields to a standard format.  Note that this does not make
        them python dates, they are still strings, but consistently formatted.
        This is for easier insertion into SQL"""

        date_cols = self.conf["date_cols"]
        for date_col, date_format in date_cols.items():
            self.etl_df = self.etl_df.with_columns(
                pl.col(date_col).str.strptime(pl.Date, format=date_format, strict=False)
            )
            # change it back to a string with consistent format
            self.etl_df = self.etl_df.with_columns(
                pl.col(date_col).dt.strftime("%m-%d-%y")
            )

    def cast_columns(self) -> None:  # todo get args from xcoms
        cast_cols = self.conf["cast_cols"]
        for cast_col, func in cast_cols.items():
            self.etl_df = self.etl_df.with_columns(
                pl.col(cast_col).map_elements(
                    lambda x: utils.casts[func["func"]](
                        x, func["default"]
                    )  # noqa: B023
                )
            )

    def additional_transformations(self) -> None:
        transformations = self.conf.get("additional_transformations", [])
        for transformation in transformations:
            transformation["args"]["df"] = self.etl_df
            function = utils.additional_transformations[transformation["function"]]
            self.etl_df = function(**transformation["args"])

    def create_primary_key(self) -> None:
        """Make a primary key field that can be used to identify new records called
        vims_primary_key."""
        primary_key_columns = self.conf["primary_key_columns"]
        concatenator = self.conf.get("pk_concatenator", "_")
        self.etl_df = self.etl_df.with_columns(
            pl.concat_str(
                *[pl.col(col).fill_null("") for col in primary_key_columns],
                separator=concatenator,
            ).alias(self.VIMS_PRIMARY_KEY)
        )

    def dedupe_insert(self) -> None:
        """
        Take a dataframe and remove the values that have already been added to the DB
        by using the previously defined vims_primary_key and then insert new records
        into the DB
        """
        table_name = self.conf["table"]["name"]

        df_existing = pl.from_pandas(
            pd.read_sql_table(table_name=table_name, con=self.DB_CONNECTION_STRING)
        )

        common_columns = np.intersect1d(self.etl_df.columns, df_existing.columns)
        df_new_records = self.etl_df[common_columns].join(
            df_existing[common_columns], on=self.VIMS_PRIMARY_KEY, how="anti"
        )

        con = self.engine.connect()

        # do all the table swapping inside a transaction
        transaction = con.begin()

        if self.use_temp_table:
            df_new_records.write_database(
                table_name=self.temp_table_name,
                connection_uri=self.DB_CONNECTION_STRING,
                if_exists="append",
            )
            # drop the old table
            con.execute(text(f"drop table {table_name}"))
            # rename the new old to the same as the old one
            con.execute(
                text(f"alter table {self.temp_table_name} rename to {table_name}")
            )
        else:
            df_new_records.write_database(
                table_name=table_name,
                connection=self.DB_CONNECTION_STRING,
                if_table_exists="append",
            )
            # drop the temp table
            con.execute(text(f"drop table {self.temp_table_name}"))

        transaction.commit()
