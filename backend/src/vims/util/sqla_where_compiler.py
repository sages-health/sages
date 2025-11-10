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

from typing import Any

from enum import Enum

import sqlalchemy as sqla

from vims.util import cast


class SqlaWhereParseError(Exception):
    pass


class SqlaWhereCompileError(Exception):
    pass


class LogicalOps(Enum):
    NOT = "$not"
    OR = "$or"
    AND = "$and"


class ComparisonOps(Enum):
    EQ = "$eq"
    NE = "$ne"
    GT = "$gt"
    GE = "$ge"
    LT = "$lt"
    LE = "$le"
    IN = "$in"
    NIN = "$nin"
    LIKE = "$like"
    ILIKE = "$ilike"
    NOTLIKE = "$notlike"
    NOTILIKE = "$notilike"
    STARTSWITH = "$startswith"
    ENDSWITH = "$endswith"
    CONTAINS = "$contains"
    IS = "$is"
    ISNOT = "$isnot"


class SQLAWhereExpression:
    @classmethod
    def parse_children(cls, to_parse: dict, top_level: bool = False):
        if not isinstance(to_parse, dict) or len(to_parse.keys()) != 1:
            raise SqlaWhereParseError(
                "Logical Expression must be a dict with one operator."
            )

        op, _ = tuple(to_parse.items())[0]
        if op in [f.value for f in LogicalOps]:
            return LogicalExpression.parse(to_parse)
        elif op in [f.value for f in ComparisonOps]:
            if top_level:
                raise SqlaWhereParseError(
                    "Comparison Expressions can not be at the root of a parse tree."
                )
            return ComparisonExpression.parse(to_parse)
        else:
            return ColumnExpression.parse(to_parse)


class LogicalExpression(SQLAWhereExpression):
    def __init__(
        self, op: LogicalOps, children: "LogicalExpression | ColumnExpression"
    ):
        self.op = op
        self.children = children

    @classmethod
    def parse(cls, to_parse: dict):
        op, children = tuple(to_parse.items())[0]

        if op == LogicalOps.NOT.value:
            if not isinstance(children, dict) or len(children) == 0:
                raise SqlaWhereParseError("NOT child must be a non-empty dictionary.")
            child = cls.parse_children(children)
            if not (
                isinstance(child, LogicalExpression)
                or isinstance(child, ColumnExpression)
            ):
                raise SqlaWhereParseError(
                    f"NOT child must be a valid Logical or Column expression. \
                        children in: {children}"
                )
            return cls(LogicalOps.NOT, child)
        elif op in [LogicalOps.AND.value, LogicalOps.OR.value]:
            if not isinstance(children, list) or len(children) == 0:
                raise SqlaWhereParseError("AND|OR child must be a non-empty list.")
            children = list(map(lambda x: cls.parse_children(x), children))
            for child in children:
                if not (
                    isinstance(child, LogicalExpression)
                    or isinstance(child, ColumnExpression)
                ):
                    raise SqlaWhereParseError(
                        "AND|OR child must be a valid Logical or Column expression."
                    )
            return cls(LogicalOps(op), children)
        else:
            raise SqlaWhereParseError(
                f"{op} is not a valid Logical Expression operator."
            )

    def __str__(self):
        if self.op is LogicalOps.NOT:
            return f"not ({str(self.children)})"
        else:
            op_str = " and " if self.op is LogicalOps.AND else " or "
            return op_str.join(list(map(lambda x: f"({str(x)})", self.children)))

    def compile(self, sqla_columns, table_metadata):
        if self.op == LogicalOps.NOT:
            compiled_child = self.children.compile(sqla_columns, table_metadata)
            return sqla.not_(compiled_child)
        elif self.op == LogicalOps.AND:
            compiled_children = list(
                map(lambda x: x.compile(sqla_columns, table_metadata), self.children)
            )
            return sqla.and_(True, *compiled_children)
        elif self.op == LogicalOps.OR:
            compiled_children = list(
                map(lambda x: x.compile(sqla_columns, table_metadata), self.children)
            )
            return sqla.or_(False, *compiled_children)


class ColumnExpression(SQLAWhereExpression):
    def __init__(self, col: str, child: "ComparisonExpression"):
        self.col = col
        self.child = child

    @classmethod
    def parse(cls, to_parse: dict):
        col, children = tuple(to_parse.items())[0]
        if not isinstance(children, dict) or len(children) == 0:
            raise SqlaWhereParseError(
                "Column Expression child must be a non-empty dictionary."
            )
        child = cls.parse_children(children)
        if not isinstance(child, ComparisonExpression):
            raise SqlaWhereParseError(
                "Column Expression child must be a valid Comparision Expression"
            )
        return ColumnExpression(col, child)

    def __str__(self):
        return f"{self.col} {str(self.child)}"

    def compile(self, sqla_columns, table_metadata):
        table_col = sqla_columns.get(self.col, None)
        if table_col is None:
            raise SqlaWhereCompileError(
                f"Error compiling query. Column: {self.col} does not "
                f"exist in target table."
            )
        col_type = table_metadata[self.col]
        return self.child.compile(table_col, lambda x: cast(x, col_type))


class ComparisonExpression(SQLAWhereExpression):
    def __init__(self, op: ComparisonOps, values: Any):
        self.op = op
        self.values = values

    @classmethod
    def parse(cls, to_parse: dict):
        op, values = tuple(to_parse.items())[0]
        op = ComparisonOps(op)
        if op in [
            ComparisonOps.LIKE,
            ComparisonOps.ILIKE,
            ComparisonOps.NOTLIKE,
            ComparisonOps.NOTILIKE,
            ComparisonOps.STARTSWITH,
            ComparisonOps.ENDSWITH,
            ComparisonOps.CONTAINS,
        ]:
            if not isinstance(values, str):
                raise SqlaWhereParseError("String comparison ops need a str arg.")
        elif op in [ComparisonOps.IN, ComparisonOps.NIN]:
            if not isinstance(values, list):
                raise SqlaWhereParseError("IN|NIN require a list arg.")
        return cls(op, values)

    def __str__(self):
        op_str = None
        if self.op is ComparisonOps.EQ:
            op_str = "=="
        elif self.op is ComparisonOps.NE:
            op_str = "!="
        elif self.op is ComparisonOps.GT:
            op_str = ">"
        elif self.op is ComparisonOps.GE:
            op_str = ">="
        elif self.op is ComparisonOps.LT:
            op_str = "<"
        elif self.op is ComparisonOps.LE:
            op_str = "<="
        elif self.op is ComparisonOps.IN:
            op_str = "in"
        elif self.op is ComparisonOps.NIN:
            op_str = "not in"
        elif self.op is ComparisonOps.LIKE:
            op_str = "like"
        elif self.op is ComparisonOps.ILIKE:
            op_str = "ilike"
        elif self.op is ComparisonOps.NOTLIKE:
            op_str = "not like"
        elif self.op is ComparisonOps.NOTILIKE:
            op_str = "not ilike"
        elif self.op is ComparisonOps.STARTSWITH:
            op_str = "starts with"
        elif self.op is ComparisonOps.ENDSWITH:
            op_str = "ends with"
        elif self.op is ComparisonOps.CONTAINS:
            op_str = "contains"
        elif self.op is ComparisonOps.IS:
            op_str = "is"
        elif self.op is ComparisonOps.ISNOT:
            op_str = "is not"

        return f"{op_str} {self.values}"

    def compile(self, col, cast_fn):
        if self.op is ComparisonOps.EQ:
            return col == cast_fn(self.values)
        elif self.op is ComparisonOps.NE:
            return col != cast_fn(self.values)
        elif self.op is ComparisonOps.GT:
            return col > cast_fn(self.values)
        elif self.op is ComparisonOps.GE:
            return col >= cast_fn(self.values)
        elif self.op is ComparisonOps.LT:
            return col < cast_fn(self.values)
        elif self.op is ComparisonOps.LE:
            return col <= cast_fn(self.values)
        elif self.op is ComparisonOps.IN:
            return col.in_(cast_fn(self.values))
        elif self.op is ComparisonOps.NIN:
            return col.not_in(cast_fn(self.values))
        elif self.op is ComparisonOps.LIKE:
            return col.like(cast_fn(self.values))
        elif self.op is ComparisonOps.ILIKE:
            return col.ilike(cast_fn(self.values))
        elif self.op is ComparisonOps.NOTLIKE:
            return col.notlike(cast_fn(self.values))
        elif self.op is ComparisonOps.NOTILIKE:
            return col.notilike(cast_fn(self.values))
        elif self.op is ComparisonOps.STARTSWITH:
            return col.startswith(cast_fn(self.values))
        elif self.op is ComparisonOps.ENDSWITH:
            return col.endswith(cast_fn(self.values))
        elif self.op is ComparisonOps.CONTAINS:
            return col.contains(cast_fn(self.values))
        elif self.op is ComparisonOps.IS:
            return col.is_(cast_fn(self.values))
        elif self.op is ComparisonOps.ISNOT:
            return col.is_not(cast_fn(self.values))


def compile(ast: "LogicalExpression | ColumnExpression"):
    pass
