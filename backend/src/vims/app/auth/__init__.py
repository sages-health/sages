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

from typing import List, Union

from base64 import b32encode, b64encode
from datetime import datetime, timedelta
from io import BytesIO

import jwt

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pyotp import TOTP, random_hex
from qrcode import make as QRCode
from sqlalchemy.exc import NoResultFound

from vims.core import Config, Inject

from ..config import config
from ..database import database
from ..database.models import tokens, user_login_tracking, user_security_settings, users
from ..model import (
    EncodedToken,
    Token,
    User,
    UserLoginTracking,
    UserPassword,
    UserPasswordToken,
    UserSecuritySettings,
)
from ..permissions import Permission
from ..roles import Role
from ..settings import Settings
from .password import PasswordContext, password

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_bearer_token(request: Request):
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, param = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported authentication type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return param


async def get_current_user_token(jwt_token: str = Depends(OAUTH2_SCHEME)):
    # Decode the JWT Token
    decoded = None
    try:
        decoded = jwt.decode(
            jwt_token,
            Config.get(Settings.JWT_SECRET_KEY),
            algorithms=[Config.get(Settings.JWT_ALGORITHM)],
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check JWT Expiration
    # FIXME: Is this redundant / does jwt.decode do this?
    expires = datetime.utcfromtimestamp(decoded["exp"])
    if expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a token from the decoded value
    query = tokens.select().where(tokens.c.id == decoded["sub"])
    token_raw = await database.fetch_one(query)

    if token_raw is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    found_token = Token.from_orm(token_raw)

    # Find the user associated with the token
    query = users.select().where(users.c.id == found_token.user)
    user_raw = await database.fetch_one(query)

    if user_raw is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token user is not valid",
        )

    print(user_raw.__init__)
    user = UserPasswordToken(**user_raw._mapping, token=found_token)
    if not user.enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is disabled",
        )
    return user


async def get_current_user(user: UserPasswordToken = Depends(get_current_user_token)):
    return User(**user.dict(by_alias=True, exclude={"token", "password"}))


class OAuth2PasswordRequestFormWithOTP(OAuth2PasswordRequestForm):
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        scope: str = Form(""),
        client_id: str = Form(None),
        client_secret: str = Form(None),
        otp: str = Form(None),
    ):
        super().__init__(
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.otp = otp


class require_permission:
    def __init__(self, permissions: Union[Permission, List[Permission]]):
        self._permissions = (
            permissions if isinstance(permissions, list) else [permissions]
        )

    def __call__(self, user: User = Depends(get_current_user)):
        permissions = list(map(lambda p: Permission(p), user.permissions.keys()))
        if Permission.ADMIN in permissions:
            return
        for permission in permissions:
            if permission in self._permissions:
                return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted"
        )


async def auth(
    config: Config = Inject(config), password: PasswordContext = Inject(password)
):
    router = APIRouter()

    token_expires: timedelta = config.get(Settings.TOKEN_EXPIRES)

    @router.post("/login")
    async def login(
        form_data: OAuth2PasswordRequestFormWithOTP = Depends(
            OAuth2PasswordRequestFormWithOTP
        ),
    ):
        # Check the user credentials against the username and password
        try:
            query = users.select().where(users.c.username == form_data.username)
            found_user = await database.fetch_one(query)
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        if not found_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        query = user_login_tracking.select().where(
            user_login_tracking.c.user == found_user.id
        )
        login_tracking = await database.fetch_one(query)
        if not login_tracking:
            login_tracking = UserLoginTracking(
                user=found_user.id, attempts=0, last_attempt=datetime.utcnow()
            )
            query = user_login_tracking.insert()
            await database.execute(query, values=login_tracking.dict())
        else:
            login_tracking = UserLoginTracking.from_orm(login_tracking)

        login_tracking.last_attempt = datetime.utcnow()

        found_user = UserPassword.from_orm(found_user)
        if login_tracking.locked_until:
            if login_tracking.locked_until > datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Account locked"
                )
        if not password.verify(form_data.password, found_user.password):
            login_tracking.attempts += 1
            if login_tracking.attempts >= Config.get(Settings.LOGIN_ATTEMPTS, 5):
                timeout_mins: timedelta = Config.get(
                    Settings.LOGIN_LOCK_TIMEOUT_MINS, 15
                )
                login_tracking.locked_until = datetime.utcnow() + timeout_mins
            query = user_login_tracking.update().where(
                user_login_tracking.c.user == found_user.id
            )
            await database.execute(query, values=login_tracking.dict())
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        if not found_user.enabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        query = user_security_settings.select().where(
            user_security_settings.c.user == found_user.id
        )
        sec_settings = await database.fetch_one(query)
        if sec_settings:
            sec_settings = UserSecuritySettings.from_orm(sec_settings)
            if sec_settings.otp_enabled and not sec_settings.secret:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unable to verify user credentials",
                )
            elif sec_settings.otp_enabled and not form_data.otp:
                login_tracking.attempts += 1
                if login_tracking.attempts >= Config.get(Settings.LOGIN_ATTEMPTS, 5):
                    timeout_mins: timedelta = Config.get(
                        Settings.LOGIN_LOCK_TIMEOUT_MINS, 15
                    )
                    login_tracking.locked_until = datetime.utcnow() + timeout_mins
                query = user_login_tracking.update().where(
                    user_login_tracking.c.user == found_user.id
                )
                await database.execute(query, values=login_tracking.dict())
                return {"otp_required": True}
            elif sec_settings.otp_enabled:
                totp = TOTP(b32encode(bytearray.fromhex(sec_settings.secret)))
                if not totp.verify(form_data.otp):
                    login_tracking.attempts += 1
                    if login_tracking.attempts >= Config.get(
                        Settings.LOGIN_ATTEMPTS, 5
                    ):
                        timeout_mins: timedelta = Config.get(
                            Settings.LOGIN_LOCK_TIMEOUT_MINS, 15
                        )
                        login_tracking.locked_until = datetime.utcnow() + timeout_mins
                    query = user_login_tracking.update().where(
                        user_login_tracking.c.user == found_user.id
                    )
                    await database.execute(query, values=login_tracking.dict())
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                    )

        login_tracking.locked_until = None
        login_tracking.attempts = 0

        query = user_login_tracking.update().where(
            user_login_tracking.c.user == found_user.id
        )
        await database.execute(query, values=login_tracking.dict())

        # Create a new token and save it to the database
        new_token = Token(user=found_user.id, expires=datetime.utcnow())
        query = tokens.insert()
        await database.execute(query, values=new_token.dict())

        # Encode the token with JWT and return
        expires = new_token.expires + token_expires
        encoded = jwt.encode(
            {"sub": str(new_token.id), "exp": expires},
            Config.get(Settings.JWT_SECRET_KEY),
            algorithm=Config.get(Settings.JWT_ALGORITHM),
        )
        return EncodedToken(
            access_token=encoded,
            token_type="bearer",
            expires=expires,
            user_id=found_user.id,
        )

    @router.get("/refresh", response_model=EncodedToken)
    async def refresh(
        current_user: UserPasswordToken = Depends(get_current_user_token),
    ):
        # Update the token expiration time in the database to the current UTC time
        updated_token = current_user.token
        updated_token.expires = datetime.utcnow()

        # Re-encode the token and return
        expires = updated_token.expires + token_expires
        encoded = jwt.encode(
            {"sub": str(updated_token.id), "exp": expires},
            Config.get(Settings.JWT_SECRET_KEY),
            algorithm=Config.get(Settings.JWT_ALGORITHM),
        )
        return EncodedToken(
            access_token=encoded,
            token_type="bearer",
            expires=expires,
            user_id=current_user.id,
        )

    @router.get("/logout", status_code=status.HTTP_202_ACCEPTED)
    async def logout(
        current_user: UserPasswordToken = Depends(get_current_user_token),
    ):
        # Delete the current token
        current_token = current_user.token
        query = tokens.delete().where(tokens.c.id == current_token.id)
        result = await database.execute(query)
        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to delete token",
            )
        return {}

    @router.get("/ping", status_code=status.HTTP_202_ACCEPTED)
    async def ping(
        current_user: UserPasswordToken = Depends(get_current_user_token),
    ):
        return True

    @router.get("/otp/check")
    async def otp_check(
        current_user: UserPasswordToken = Depends(get_current_user_token),
    ):
        query = user_security_settings.select().where(
            user_security_settings.c.user == current_user.id
        )
        sec_settings = await database.fetch_one(query)
        if not sec_settings:
            return {"otp_enabled": False}
        else:
            sec_settings = UserSecuritySettings.from_orm(sec_settings)
            return {"otp_enabled": sec_settings.otp_enabled}

    @router.post("/otp/enable", status_code=status.HTTP_202_ACCEPTED)
    async def otp_enable(
        current_user: UserPasswordToken = Depends(get_current_user_token),
        otp: int = Form(...),
    ):
        query = user_security_settings.select().where(
            user_security_settings.c.user == current_user.id
        )
        sec_settings = await database.fetch_one(query)
        if not sec_settings:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No security settings found for user",
            )

        sec_settings = UserSecuritySettings.from_orm(sec_settings)
        if not sec_settings.secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid security settings found for user",
            )

        totp = TOTP(b32encode(bytearray.fromhex(sec_settings.secret)))
        if not totp.verify(otp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP passcode"
            )

        sec_settings.otp_enabled = True

        query = user_security_settings.update().where(
            user_security_settings.c.user == current_user.id
        )
        await database.execute(query, sec_settings.dict())

        return True

    @router.get("/otp/disable", status_code=status.HTTP_202_ACCEPTED)
    async def otp_disable(
        current_user: UserPasswordToken = Depends(get_current_user_token),
    ):
        query = user_security_settings.select().where(
            user_security_settings.c.user == current_user.id
        )
        sec_settings = await database.fetch_one(query)
        if not sec_settings:
            sec_settings = UserSecuritySettings(user=current_user.id, otp_enabled=False)
            query = user_security_settings.insert()
            await database.execute(query, sec_settings.dict())
        else:
            sec_settings = UserSecuritySettings.from_orm(sec_settings)

        sec_settings.otp_enabled = False

        query = user_security_settings.update().where(
            user_security_settings.c.user == current_user.id
        )
        await database.execute(query, sec_settings.dict())

        return True

    @router.get(
        "/otp/disable/{user_id}",
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=[Depends(require_permission([Permission.ADMIN]))],
    )
    async def otp_disable_user(user_id: str):
        query = user_security_settings.select().where(
            user_security_settings.c.user == user_id
        )
        sec_settings = await database.fetch_one(query)
        if not sec_settings:
            sec_settings = UserSecuritySettings(user=user_id, otp_enabled=False)
            query = user_security_settings.insert()
            await database.execute(query, sec_settings.dict())
        else:
            sec_settings = UserSecuritySettings.from_orm(sec_settings)

        sec_settings.otp_enabled = False

        query = user_security_settings.update().where(
            user_security_settings.c.user == user_id
        )
        await database.execute(query, sec_settings.dict())

        return True

    @router.get("/otp/generate")
    async def otp_generate(
        current_user: UserPasswordToken = Depends(get_current_user_token),
    ):
        query = user_security_settings.select().where(
            user_security_settings.c.user == current_user.id
        )
        sec_settings = await database.fetch_one(query)
        if not sec_settings:
            sec_settings = UserSecuritySettings(user=current_user.id, otp_enabled=False)
            query = user_security_settings.insert()
            await database.execute(query, sec_settings.dict())

        sec_settings = UserSecuritySettings.from_orm(sec_settings)
        if not sec_settings.secret or not sec_settings.otp_enabled:
            sec_settings.secret = random_hex()

        query = user_security_settings.update().where(
            user_security_settings.c.user == current_user.id
        )
        await database.execute(query, sec_settings.dict())

        totp = TOTP(b32encode(bytearray.fromhex(sec_settings.secret)))
        qr_code = QRCode(
            totp.provisioning_uri(name=current_user.id, issuer_name="VIM/SAGES")
        )
        img_byte_arr = BytesIO()
        qr_code.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()

        return Response(content=b64encode(img_byte_arr), media_type="image/png")

    return router


__all__ = [
    "auth",
    "get_current_user_token",
    "get_current_user",
    "password",
    "PasswordContext",
    "Permission",
    "require_permission",
    "Role",
]
