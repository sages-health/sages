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

from typing import Dict, List, Optional

from datetime import datetime
from uuid import uuid4

from pydantic import Field

from .base import BaseModel
from .token import Token


class UserLoginTracking(BaseModel):
    user: str
    attempts: int
    last_attempt: datetime
    locked_until: datetime | None = None


class UserChangePassword(BaseModel):
    password: str


class UserPasswordReset(BaseModel):
    token: str
    password: str


class UserSecuritySettings(BaseModel):
    user: str
    otp_enabled: bool = False
    secret: str | None = None


class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str | None = None
    organization: str | None = None
    phone_number: str
    enabled: bool = True
    remote: bool = False
    roles: Dict[str, bool] = Field(default_factory=dict)
    groups: List[str] = Field(default_factory=list)


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: str | None = None
    current_password: str | None = None


class UserInternal(UserBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    permissions: Dict[str, bool] = Field(default_factory=dict)
    last_modified: datetime | None = None


class UserInternalPassword(UserInternal):
    password: str
    password_last_updated: datetime | None = None
    password_history: List[str] = Field(default_factory=list)


class User(UserInternal):
    created: datetime = Field(default_factory=datetime.utcnow)
    password_last_updated: datetime | None = None


class UserPassword(User):
    password: str
    password_last_updated: datetime | None = None
    password_history: List[str] = Field(default_factory=list)


class UserPasswordToken(UserPassword):
    token: Token


class UserWithMetadata(User):
    locked_until: Optional[datetime | None] = None
    otp_enabled: Optional[bool | None] = None
