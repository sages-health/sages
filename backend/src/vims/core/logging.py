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

from typing import Any, Literal, Mapping, Optional, Tuple, Union

import logging
import re

from logging import Formatter, Logger, LogRecord, getLogger
from re import Pattern

STANDARD_SEPARATOR = re.compile(r"\.")
ATTRIBUTE_START = re.compile(r"[\w]")

USE_COLOR = False
try:
    from colorama import init as colorama_init

    USE_COLOR = True
except ImportError:
    pass


def color_init(**kwargs):
    if USE_COLOR:
        colorama_init(**kwargs)


class Style:
    try:
        from colorama import Style

        BRIGHT = Style.BRIGHT
        DIM = Style.DIM
        NORMAL = Style.NORMAL
        RESET_ALL = Style.RESET_ALL

        STYLE_NAMES = {BRIGHT: "BRIGHT", DIM: "DIM", NORMAL: "NORMAL"}
    except ImportError:
        BRIGHT = ""
        DIM = ""
        NORMAL = ""
        RESET_ALL = ""

        STYLE_NAMES = {"": "UNKNOWN"}

    ALL_STYLES = {BRIGHT, DIM, NORMAL}

    @classmethod
    def wrap(cls, style: str, value: Any):
        if style not in cls.ALL_STYLES:
            raise KeyError(f'Invalid style "{cls.STYLE_NAMES.get(style, "UNKNOWN")}"')
        return f"{style}{value}{cls.NORMAL}"

    @classmethod
    def bright(cls, value: Any):
        return cls.wrap(cls.BRIGHT, value)

    @classmethod
    def dim(cls, value: Any):
        return cls.wrap(cls.DIM, value)

    @classmethod
    def normal(cls, value: Any):
        return cls.wrap(cls.NORMAL, value)


class AnsiColors:
    BLACK = ""
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    MAGENTA = ""
    CYAN = ""
    WHITE = ""
    RESET = ""

    LIGHTBLACK_EX = ""
    LIGHTRED_EX = ""
    LIGHTGREEN_EX = ""
    LIGHTYELLOW_EX = ""
    LIGHTBLUE_EX = ""
    LIGHTMAGENTA_EX = ""
    LIGHTCYAN_EX = ""
    LIGHTWHITE_EX = ""

    @classmethod
    @property
    def ALL_COLORS(cls):
        return {
            cls.BLACK,
            cls.RED,
            cls.GREEN,
            cls.YELLOW,
            cls.BLUE,
            cls.MAGENTA,
            cls.CYAN,
            cls.WHITE,
            cls.LIGHTBLACK_EX,
            cls.LIGHTRED_EX,
            cls.LIGHTGREEN_EX,
            cls.LIGHTYELLOW_EX,
            cls.LIGHTBLUE_EX,
            cls.LIGHTMAGENTA_EX,
            cls.LIGHTCYAN_EX,
            cls.LIGHTWHITE_EX,
        }

    @classmethod
    @property
    def COLOR_NAMES(cls):
        return {
            cls.BLACK: "BLACK",
            cls.RED: "RED",
            cls.GREEN: "GREEN",
            cls.YELLOW: "YELLOW",
            cls.BLUE: "BLUE",
            cls.MAGENTA: "MAGENTA",
            cls.CYAN: "CYAN",
            cls.WHITE: "WHITE",
            cls.RESET: "RESET",
            cls.LIGHTBLACK_EX: "LIGHTBLACK",
            cls.LIGHTRED_EX: "LIGHTRED",
            cls.LIGHTGREEN_EX: "LIGHTGREEN",
            cls.LIGHTYELLOW_EX: "LIGHTYELLOW",
            cls.LIGHTBLUE_EX: "LIGHTBLUE",
            cls.LIGHTMAGENTA_EX: "LIGHTMAGENTA",
            cls.LIGHTCYAN_EX: "LIGHTCYAN",
            cls.LIGHTWHITE_EX: "LIGHTWHITE",
            "": "UNKNOWN",
        }

    @classmethod
    def wrap(
        cls,
        color: str,
        value: Any,
        style: str = Style.NORMAL,
    ):
        if color not in cls.ALL_COLORS:
            raise KeyError(f'Invalid color "{cls.COLOR_NAMES.get(color, "UNKNOWN")}"')
        return Style.wrap(style, f"{color}{value}{cls.RESET}")

    @classmethod
    def black(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.BLACK, value, style=style)

    @classmethod
    def red(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.RED, value, style=style)

    @classmethod
    def green(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.GREEN, value, style=style)

    @classmethod
    def yellow(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.YELLOW, value, style=style)

    @classmethod
    def blue(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.BLUE, value, style=style)

    @classmethod
    def magenta(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.MAGENTA, value, style=style)

    @classmethod
    def cyan(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.CYAN, value, style=style)

    @classmethod
    def white(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.WHITE, value, style=style)

    @classmethod
    def light_black(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.LIGHTBLACK_EX, value, style=style)

    @classmethod
    def light_red(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.LIGHTRED_EX, value, style=style)

    @classmethod
    def light_green(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.LIGHTGREEN_EX, value, style=style)

    @classmethod
    def light_yellow(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.LIGHTYELLOW_EX, value, style=style)

    @classmethod
    def light_blue(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.LIGHTBLUE_EX, value, style=style)

    @classmethod
    def light_magenta(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.LIGHTMAGENTA_EX, value, style=style)

    @classmethod
    def light_cyan(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.LIGHTCYAN_EX, value, style=style)

    @classmethod
    def light_white(cls, value: Any, style: str = Style.NORMAL):
        return cls.wrap(cls.LIGHTWHITE_EX, value, style=style)


class Back(AnsiColors):
    try:
        from colorama import Back

        BLACK = Back.BLACK
        RED = Back.RED
        GREEN = Back.GREEN
        YELLOW = Back.YELLOW
        BLUE = Back.BLUE
        MAGENTA = Back.MAGENTA
        CYAN = Back.CYAN
        WHITE = Back.WHITE
        RESET = Back.RESET

        LIGHTBLACK_EX = Back.LIGHTBLACK_EX
        LIGHTRED_EX = Back.LIGHTRED_EX
        LIGHTGREEN_EX = Back.LIGHTGREEN_EX
        LIGHTYELLOW_EX = Back.LIGHTYELLOW_EX
        LIGHTBLUE_EX = Back.LIGHTBLUE_EX
        LIGHTMAGENTA_EX = Back.LIGHTMAGENTA_EX
        LIGHTCYAN_EX = Back.LIGHTCYAN_EX
        LIGHTWHITE_EX = Back.LIGHTWHITE_EX
    except ImportError:
        pass


class Fore(AnsiColors):
    try:
        from colorama import Fore

        BLACK = Fore.BLACK
        RED = Fore.RED
        GREEN = Fore.GREEN
        YELLOW = Fore.YELLOW
        BLUE = Fore.BLUE
        MAGENTA = Fore.MAGENTA
        CYAN = Fore.CYAN
        WHITE = Fore.WHITE
        RESET = Fore.RESET

        LIGHTBLACK_EX = Fore.LIGHTBLACK_EX
        LIGHTRED_EX = Fore.LIGHTRED_EX
        LIGHTGREEN_EX = Fore.LIGHTGREEN_EX
        LIGHTYELLOW_EX = Fore.LIGHTYELLOW_EX
        LIGHTBLUE_EX = Fore.LIGHTBLUE_EX
        LIGHTMAGENTA_EX = Fore.LIGHTMAGENTA_EX
        LIGHTCYAN_EX = Fore.LIGHTCYAN_EX
        LIGHTWHITE_EX = Fore.LIGHTWHITE_EX
    except ImportError:
        pass


class Colors:
    @classmethod
    @property
    def Fore(cls):
        return Fore

    @classmethod
    @property
    def Back(cls):
        return Back

    @classmethod
    @property
    def Style(cls):
        return Style


class StandardLogRecord(LogRecord):
    def getMessage(self) -> str:
        msg = str(self.msg)
        if self.args and isinstance(self.args, tuple):
            kwargs, args = {}, self.args
            if isinstance(args[-1], Mapping):
                kwargs, args = args[-1], args[0:-1]
            msg = msg.format(*args, **kwargs)
        return msg

    @classmethod
    def create(cls, *args, **kwds):
        return cls(*args, **kwds)


class StandardFormatter(Formatter):
    def __init__(
        self,
        width: Optional[Mapping[str, int]] = {},
        align: Optional[Mapping[str, Literal["<", ">", "^"]]] = {},
        short: Optional[Mapping[str, bool]] = {},
        color: Optional[Mapping[str, Mapping[Any, str]]] = {},
        split: Optional[Mapping[str, Union[str, Pattern]]] = {},
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = "%",
        validate: bool = True,
    ) -> None:
        self.__width = width
        self.__align = align
        self.__short = short
        self.__color = color

        def compile_patterns(
            item: Tuple[str, Union[str, Pattern]]
        ) -> Tuple[str, Pattern]:
            return (
                item[0],
                item[1]
                if isinstance(item[1], Pattern)
                else re.compile(re.escape(f"{item[1]}")),
            )

        self.__split = split
        self.__pattern = dict(map(compile_patterns, split.items()))

        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate)

    def format(self, record: LogRecord) -> str:
        attributes = [
            attr
            for attr in dir(record)
            if not attr.startswith("_") and attr != "getMessage"
        ]

        if USE_COLOR and hasattr(record, "color_message"):
            setattr(record, "message", record.getMessage())
            setattr(record, "msg", getattr(record, "color_message"))

        for attr in attributes:
            raw = getattr(record, attr)
            if not isinstance(raw, str):
                continue
            value = raw
            width = self.__width.get(attr)
            color = self.__color.get(attr)
            align = self.__align.get(attr, "<")
            separator = self.__split.get(attr, ".")
            separator = "." if isinstance(separator, Pattern) else separator
            pattern = self.__pattern.get(attr, STANDARD_SEPARATOR)

            if self.__short.get(attr) is not None:
                if width is None:
                    raise RuntimeError(f"Shorten requires width ({attr})")

                if len(value) > width:
                    value = pattern.split(value)
                    combined = ".".join(value)
                    index = 0
                    max_index = len(value) - 1
                    while len(combined) > width and index < max_index:
                        value[index] = value[index][0]
                        combined = separator.join(value)
                        index = index + 1
                    value = combined

            if width:
                if len(value) > width:
                    value = value[-1 * width :]
                    # Trim off any prefix separators
                    match = ATTRIBUTE_START.search(value)
                    if match:
                        value = value[match.start(0) :]
                value = f"{value:{align}{width}}"

            if color:
                value = f'{color.get(raw, "")}{value}{Style.RESET_ALL}'

            setattr(record, attr, value)

        return super().format(record)


def logging_init(**kwargs):
    base = {"autoreset": True}
    base.update(kwargs)
    color_init(**base)

    root = getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setFormatter(
        StandardFormatter(
            width={"levelname": 8, "name": 20},
            short={"name": True},
            color={
                "levelname": {
                    logging.getLevelName(logging.CRITICAL): Fore.MAGENTA,
                    logging.getLevelName(logging.ERROR): Fore.RED,
                    logging.getLevelName(logging.WARNING): Fore.YELLOW,
                    logging.getLevelName(logging.INFO): Fore.BLUE,
                    logging.getLevelName(logging.DEBUG): Fore.GREEN,
                }
            },
            fmt="\r{asctime} <{process}> [{levelname}] {name} : {message}",
            style="{",
        )
    )
    root.addHandler(ch)


__all__ = [
    "getLogger",
    "Logger",
    "logging_init",
]
