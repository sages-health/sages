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

import re
import tempfile

from pathlib import Path

import pandas as pd
import polars as pl
import sqlalchemy

from vims.app.config import Config
from vims.app.settings import Settings

json_input_to_sqlalchemy_types = {
    "float": sqlalchemy.Float,
    "date": sqlalchemy.Date,
    "integer": sqlalchemy.Integer,
    "string": sqlalchemy.String,
    "text": sqlalchemy.UnicodeText,
}

json_input_sql_types_as_strings = {
    "float": "float",
    "date": "date",
    "integer": "smallint",
    "string": "varchar(500)",
    "text": "text",
}


def build_table_from_dict(table_definition: dict):
    cols = []
    for col_name, col_type in table_definition["columns"].items():
        cols.append(
            sqlalchemy.Column(
                col_name, json_input_to_sqlalchemy_types[col_type.lower()]
            )
        )

    # add the vims_primary_key column here
    model = sqlalchemy.Table(
        table_definition["name"],
        sqlalchemy.MetaData(),
        *cols,
        sqlalchemy.Column(
            Config.get(Settings.ETL_PRIMARY_KEY_COLUMN_NAME),
            sqlalchemy.String,
            primary_key=True,
        ),
    )

    return model


def custom_read_excel(filename: str, **kwargs: dict) -> pl.DataFrame:
    df = pd.read_excel(filename, **kwargs)
    # have to write this to a csv and then load from there,
    # polars.from_pandas doesn't work with mixed column types:
    # https://stackoverflow.com/questions/71657556/
    # error-while-converting-pandas-dataframe-to-polars-dataframe-pyarrow-lib-arrowty
    tmp = tempfile.NamedTemporaryFile()
    path = Path(tmp.name)
    with path.open("w+b") as f:
        df.to_csv(f)
        f.seek(0)
        df = pl.read_csv(f)
        # remove the unneeded auto increment column with no name that gets created
        df = df.drop([""])

    return df


def custom_csv_or_excel(filename: str, **kwargs: dict) -> pl.DataFrame:
    """
    Use this reader function if you want to accept either csv or anything that
    pd.read_excel accepts (xls, xlsx, xlsm, xlsb, odf, ods, odt)

    :param filename:
    :param kwargs:
    :return:
    """
    if ".csv" in filename:
        df = pl.read_csv(filename, **kwargs)
    else:
        try:
            df = custom_read_excel(filename, **kwargs)
        except Exception:
            raise ValueError(
                f"Filetype appears to be readable by neither pl.read_csv or "
                f"pd.read_excel. Filename: {filename}"
            )
    return df


def date_conv(tt: str) -> str:
    ts = tt
    date_parts = ts.split("/")
    if date_parts and len(date_parts) > 2:
        year = date_parts[2] if len(date_parts[2]) == 4 else "20" + date_parts[2]
        month = date_parts[1] if len(date_parts[1]) == 2 else "0" + date_parts[1]
        day = date_parts[0] if len(date_parts[0]) == 2 else "0" + date_parts[0]
        ts = month + "/" + day + "/" + year
        if ts != "":
            return ts
        else:
            return None


def custom_read_latin_csv(filename: str, **kwargs: dict) -> pl.DataFrame:
    df = pd.read_csv(filename, converters={"FECHA": date_conv}, **kwargs)
    df = pl.from_pandas(df)

    return df


def read_excel_all_sheets(filename: str, **kwargs: dict) -> pl.DataFrame:
    """Reads all of the sheets in an Excel workbook into one DataFrame.
    Assumes that all the sheets contain the same columns"""
    all_sheets = pl.read_excel(filename, sheet_id=0, **kwargs)
    # diagnonal means the dataframes don't have to be the same shape
    return pl.concat(all_sheets.values(), how="diagonal")


def cast_int_with_default(value: str, default: int = 0) -> int:
    """Cast the value to an integer, if an error occurs
    return the default value"""
    try:
        return int(value)
    except ValueError:
        return default
    except TypeError:
        return default


def cast_age_with_units(value: str, default: float = 0.0) -> float:
    """
    Sometimes age is given in:
    months, signified by a letter 'm' after the number,
    days, signified by a letter 'd' after the number,
    years, signified by a letter 'a' after the number.
    Convert these to fraction of years
    """
    if isinstance(value, str) and "m" in value.lower():
        return float(int(re.sub("\\D", "", value)) / 12)
    elif isinstance(value, str) and "d" in value.lower():
        return float(int(re.sub("\\D", "", value)) / 365)
    elif isinstance(value, str) and "a" in value.lower():
        return float(int(re.sub("\\D", "", value)))
    else:
        try:
            return float(value)
        except ValueError:
            return default
        except TypeError:
            return default


def cast_float_with_default(value: str, default: float = 0.0) -> float:
    """Cast the value to a float, if an error occurs
    return the default value"""
    try:
        return float(value)
    except ValueError:
        return default
    except TypeError:
        return default


def concatenate_checkbox_columns(
    df: pl.DataFrame, cols_to_concat: list[str], new_col_name: str, separator: str = ";"
) -> pl.DataFrame:
    """
    Takes a list of 'checkbox' style boxes and converts them into 1 new column
    which is a concatenation of the columns which were checked off
    """
    # convert check boxes to either the name of the column or an empty string
    for col in cols_to_concat:
        df = df.with_columns(
            pl.when(pl.col(col).is_not_null()).then(col).otherwise("").keep_name()
        )

    # make new column with values combined as a string, then remove empty elements
    df = df.with_columns(pl.concat_list(cols_to_concat).alias(new_col_name))
    df = df.with_columns(
        pl.col(new_col_name).list.eval(pl.element().filter(pl.element() != ""))
    )

    # change the list to a string with the specified separator
    return df.with_columns(
        pl.col(new_col_name).cast(pl.List(pl.Utf8)).list.join(separator=separator)
    )


def new_column(
    df: pl.DataFrame, column_name: str, column_value: [int, str]
) -> pl.DataFrame:
    """
    Create new column with same value for all rows
    """
    df = df.with_columns(pl.lit(column_value).alias(column_name))

    return df


def rename_column_append_previous_column(
    df: pl.DataFrame, cols: list[str], append_str: str
) -> pl.DataFrame:
    """Take a set of column names and renames them to be the
    previous column name + a specified string"""
    for col in cols:
        col_index = df.columns.index(col)
        prev_col = df.columns[col_index - 1]
        df = df.rename({col: f"{prev_col}_{append_str}"})

    return df


def rename_column_dict(df: pl.DataFrame, replace_dict: dict[str, str]) -> pl.DataFrame:
    """Take a set of column names and renames them to be the
    previous column name + a specified string"""
    df = df.rename(replace_dict)

    return df


DEFAULT_COLUMN_NAME_REPLACEMENTS = {
    re.compile(r"[\s/:-]+"): "_",
    re.compile(r"[()#.,]+"): "",
}

DEFAULT_CELL_VALUE_REPLACEMENTS_NAMES = [
    "no_refiere",
    "no_aplica",
    "no_indica",
    "no_se_distingue",
    "mal_escrita",
    "sin_dato",
]

cell_replacements = {
    "no_refiere": (r"(?i)\s*NO\s*REFIERE\s*", None),
    "no_aplica": (r"(?i)\s*NO\s*APLICA\s*", None),
    "no_indica": (r"(?i)\s*NO\s*INDICA\s*", None),
    "no_refirio_muestra": (r"(?i)\s*NO\s*REFIRIÓ\s*MUESTRA\s*", None),
    "no_se_distingue": (r"(?i)\s*NO\s*SE\s*DISTINGUE\s*", None),
    "no_se_realizo": (r"(?i)\s*NO\s*SE\s*REALIZ[OÓ]\s*", None),
    "mal_escrita": (r"(?i)\s*MAL\s*ESCRITA\s*", None),
    "sin_dato": (r"(?i)\s*SIN\s*DATO\s*", None),
    "?": (r"[?]+", None),
    "sd": (r"^SD$", None),
}

column_name_replacements = {
    "all": {
        re.compile(r"[\s/:-]+"): "_",
        re.compile(r"[()#.,]+"): "",
        re.compile(r"[_]+"): "_",
        re.compile(r"[_]+$"): "",
        re.compile(r"^[_]+"): "",
    }
}

readers = {
    "pd_read_excel": pd.read_excel,
    "pl_read_excel": pl.read_excel,
    "read_all_excel_sheets": read_excel_all_sheets,
    "custom_read_excel": custom_read_excel,
    "custom_read_latin_csv": custom_read_latin_csv,
    "pl_read_csv": pl.read_csv,
    "csv_or_excel": custom_csv_or_excel,
}

casts = {
    "cast_int": cast_int_with_default,
    "cast_float": cast_float_with_default,
    "cast_age_with_units": cast_age_with_units,
}

additional_transformations = {
    "checkbox_to_list": concatenate_checkbox_columns,
    "new_column": new_column,
}

col_rename_funcs = {
    "append_prev_name": rename_column_append_previous_column,
    "rename_dict": rename_column_dict,
}

configuration = {
    "bd_malaria": {
        "table": "bd_malaria",
        "primary_key_columns": ["CODIGO_CORRELATIVO", "FECHA"],  # todo is this ok?
        "column_name_replacements": "all",
        "reader": "read_all_excel_sheets",
        "reader_arguments": {
            "xlsx2csv_options": {
                "ignore_formats": [
                    "float",
                ],
            },
            "read_csv_options": {
                "infer_schema_length": 1000000000000,
                "try_parse_dates": False,
                "skip_rows": 1,
            },
        },
        "cast_cols": {
            "SEMANA": ("cast_int", None),
            "EDAD": ("cast_int", None),
        },
        "cell_value_replacements": [
            "no_refiere",
            "no_aplica",
            "no_se_distingue",
            "mal_escrita",
        ],
        "date_cols": {
            "INICIO_SINTOMAS": "%d/%m/%Y",
            "FECHA_DE_TOMA": "%d/%m/%Y",
            "RECEPCIÓN": "%d/%m/%Y",
            "FECHA": "%d/%m/%Y",
        },
    },
    "base_de_datos_arbo": {
        "table": "base_de_datos_arbo",
        "primary_key_columns": ["Código", "Tipo_de_muestras_entrantes"],
        "column_name_replacements": "all",
        "column_rename_func": {
            "function": "append_prev_name",
            "func_args": {
                "cols": [
                    "Protocolo",
                    "Protocolo1",
                    "Protocolo2",
                    "Protocolo3",
                    "Protocolo4",
                    "Protocolo5",
                    "Protocolo6",
                    "Protocolo7",
                    "Protocolo8",
                    "Protocolo9",
                    "Protocolo10",
                    "Protocolo11",
                ],
                "append_str": "Protocolo",
            },
        },
        "reader": "custom_read_excel",
        "cast_cols": {
            # m in the age field means months, not years
            "Edad": ("cast_age_with_units", None),
            "Días_con_síntomas": ("cast_int", None),
            "Semana_epidemiológica": ("cast_int", None),
            "Semana_de_embarazo": ("cast_int", None),
            "No_de_Mes_Por_año": ("cast_int", None),
            "Días_transcurridos_desde_el_procesamiento": (
                "cast_int",
                None,
            ),
            "Días_transcurridos_desde_entrada_de_la_muestra": (
                "cast_int",
                None,
            ),
        },
        "cell_value_replacements": [
            "no_refiere",
            "no_aplica",
            "no_se_distingue",
            "mal_escrita",
        ],
        "date_cols": {
            "Fecha_de_Inicio_de_síntomas": "%d/%m/%Y",
            "Fecha_de_toma_de_muestra": "%d/%m/%Y",
            "Fecha_de_Recepción_en_el_Laboratorio": "%d/%m/%Y",
            "Fecha_de_procesamiento": "%d/%m/%Y",
            "Fecha_de_actualización_a_la_nube": "%d/%m/%Y",
        },
        "reader_arguments": {
            "skiprows": 9,
        },
        "additional_transformations": [
            {
                "function": "checkbox_to_list",
                "args": {
                    "cols_to_concat": [
                        "Fiebre",
                        "conjuntivitis_no_purulenta",
                        "cefalea",
                        "astenia",
                        "dolor_retro_orbitario",
                        "anorexia",
                        "vómitos",
                        "vómitos_con_sangre",
                        "hemorragia_de_encías",
                        "hemorragia_vaginal",
                        "hemorragia_urinaria",
                        "enterorragia",
                        "melena",
                        "petequias",
                        "episitaxis",
                        "mialgias",
                        "piel_fría",
                        "rash",
                        "sudoración",
                        "tos",
                        "diarrea",
                        "dolor_abdominal",
                        "edema_en_articulaciones",
                        "artralgias",
                        "artritis",
                        "equimosis",
                        "congestión_nasal",
                        "adenopatías",
                        "dolor_de_cuerpo",
                        "Náusea",
                        "escalofríos",
                    ],
                    "separator": "; ",
                    "new_col_name": "transformed_symptoms",
                },
            },
        ],
    },
    "base_seq": {
        "table": "base_seq",
        "col_rename": {},
        "primary_key_columns": ["ID_SEQ", "ID_COVID"],
        "column_name_replacements": "all",
        "reader": "pl_read_excel",
        "reader_arguments": {
            "sheet_id": 2,
            "xlsx2csv_options": {
                "ignore_formats": [
                    "float",
                ]
            },
            "read_csv_options": {
                "infer_schema_length": 1000000000000,
                "try_parse_dates": False,
            },
        },
        "cell_value_replacements": [
            "no_refiere",
            "no_aplica",
            "no_se_distingue",
            "mal_escrita",
        ],
        "date_cols": {
            "FECHA_DE_NACIMIENTO": "%m/%d/%Y",
            "FECHA_SECUENCIADO_LOCAL": "%m/%d/%Y",
            "FECHA_INICIO_DE_SÍNTOMAS": "%m/%d/%Y",
            "FECHA_DE_TOMA_DE_MUESTRA": "%m/%d/%Y",
            "FECHA_INGRESO_DE_MUESTRA": "%m/%d/%Y",
            "FECHA_DE_PROCESO_VOC": "%m/%d/%Y",
            "FECHA_ENVÍO_A_SECUENCIAR_SEQ": "%m/%d/%Y",
            "FECHA_RECEPCIÓN_DE_RESULTADO": "%m/%d/%Y",
        },
        "cast_cols": {
            "SEMANA_EPIDEMIOLOGICA": ("cast_int", None),
            "ID_SEQ": ("cast_int", None),
            "ID_COVID": ("cast_int", None),
            "CT_RT_PCR": ("cast_int", None),
            "AÑOS": ("cast_int", None),
            "MESES": ("cast_int", None),
            "DÍAS": ("cast_int", None),
            "DOSIS": ("cast_int", None),
            "DOSIS_REFUERZO": ("cast_int", None),
        },
    },
    "ira": {
        "table": {
            "name": "ira",
            "columns": {
                "ew": "date",
                "sf1": "integer",
                "sf2": "integer",
                "sf3": "integer",
                "sf4": "integer",
                "sf5": "integer",
                "sf6": "integer",
                "cf1": "integer",
                "cf2": "integer",
                "cf3": "integer",
                "cf4": "integer",
                "cf5": "integer",
                "cf6": "integer",
                "info": "string",
                "fac": "string",
            },
        },
        "col_rename": {},
        "primary_key_columns": ["info"],  # todo this
        "column_name_replacements": "all",
        "reader": "pl_read_csv",
        "reader_arguments": {},
        "cell_value_replacements": [
            "no_refiere",
            "no_aplica",
            "no_se_distingue",
            "mal_escrita",
        ],
        "date_cols": {"ew": "%Y-%m-%d"},
        "cast_cols": {},
    },
    "cei": {
        "table": {
            "name": "cei",
            "columns": {
                "ddn": "date",
                "en": "string",
                "fi": "date",
                "sc": "string",
                "tdp": "string",
                "ddi": "integer",
                "nom": "integer",
                "ap": "string",
                "g": "string",
                "eda": "integer",
                "pfr": "string",
                "pfrt": "string",
                "info": "string",
                "fac": "string",
            },
        },
        "col_rename": {},
        "primary_key_columns": ["info"],  # todo this
        "column_name_replacements": "all",
        "reader": "pl_read_csv",
        "reader_arguments": {},
        "cell_value_replacements": [
            "no_refiere",
            "no_aplica",
            "no_se_distingue",
            "mal_escrita",
        ],
        "date_cols": {"ddn": "%Y-%m-%d", "fi": "%Y-%m-%d"},
        "cast_cols": {},
    },
}
