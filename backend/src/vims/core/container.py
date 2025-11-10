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

from typing import Any, Awaitable, Callable, DefaultDict, Dict, Hashable, List, Optional

import inspect

from collections import defaultdict
from enum import Enum
from inspect import Parameter


class Scope(Enum):
    SINGLETON = "SINGLETON"
    INSTANCED = "INSTANCED"


def identity_resolver(values: List):
    len_values = len(values)
    if len_values > 1:
        return values
    elif len_values == 1:
        return values[0]
    else:
        return None


class Dependency:
    UNSET = object()
    REGISTRY: DefaultDict[Hashable, List[Callable[..., Any]]] = defaultdict(list)
    LIFETIME: Dict[Hashable, Scope] = {}
    RESOLVER: DefaultDict[Hashable, Callable[[List[Any]], Any]] = defaultdict(
        lambda: identity_resolver
    )
    INSTANCE: Dict[Hashable, Any] = {}

    def __init__(self, reference: Hashable) -> None:
        self._reference = reference

    @property
    def reference(self):
        return self._reference

    @classmethod
    def decorate(cls, ref: Hashable):
        def register_decorator(decorator: Callable[[List[Any]], Any]):
            cls.RESOLVER[ref] = decorator
            return decorator

        return register_decorator

    @classmethod
    def register(
        cls,
        ref: Optional[Hashable] = None,
        factory: Optional[Callable[..., Any]] = None,
        scope: Scope = Scope.SINGLETON,
    ):
        def register_factory(factory: Callable[..., Any]):
            key = ref if ref else factory
            cls.REGISTRY[key].append(factory)
            if not cls.LIFETIME.get(key):
                cls.LIFETIME[key] = scope
            return factory

        return register_factory if factory is None else register_factory(factory)

    @classmethod
    async def resolve(cls, ref: Hashable, *args, **kwargs):
        scope = cls.LIFETIME.get(ref, Scope.SINGLETON)
        instance = cls.INSTANCE.get(ref, cls.UNSET)

        if scope == Scope.INSTANCED or instance == cls.UNSET:

            factories = (
                [ref] if isinstance(ref, Callable) else cls.REGISTRY.get(ref, [])
            )
            if len(factories) == 0:
                raise RuntimeError(f"Undefined dependency '{ref}'")
            values = []
            for factory in factories:
                dkwargs: Dict[str, Any] = {}
                for name, param in inspect.signature(factory).parameters.items():
                    if param.default != Parameter.empty and isinstance(
                        param.default, Dependency
                    ):
                        dkwargs[name] = await cls.resolve(param.default.reference)
                value = factory(*args, **kwargs, **dkwargs)
                if isinstance(value, Awaitable):
                    value = await value
                values.append(value)

            instance = cls.RESOLVER[ref](values)
            if scope == Scope.SINGLETON:
                cls.INSTANCE[ref] = instance

        return instance

    @classmethod
    def provider(cls, ref: Hashable, *args, **kwargs):
        async def resolve_reference():
            return await cls.resolve(ref, *args, **kwargs)

        return resolve_reference


def Inject(ref: Hashable):
    return Dependency(ref)


def Provider(ref: Hashable, *args, **kwargs):
    return Dependency.provider(ref, *args, **kwargs)
