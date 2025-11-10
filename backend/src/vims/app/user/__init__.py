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

import smtplib

from datetime import datetime, timedelta
from email.mime.text import MIMEText

import jwt

from fastapi import APIRouter, Depends, HTTPException, status

from vims.core import Config, Dependency, Inject, Scope

from ..auth import (
    PasswordContext,
    Permission,
    Role,
    get_current_user,
    password,
    require_permission,
)
from ..database import database
from ..database.models import user_login_tracking, user_security_settings, users
from ..model import (
    User,
    UserChangePassword,
    UserCreate,
    UserInternal,
    UserInternalPassword,
    UserLoginTracking,
    UserPassword,
    UserPasswordReset,
    UserSecuritySettings,
    UserUpdate,
    UserWithMetadata,
)
from ..role import role_config
from ..settings import Settings


def synchronize_roles(
    user: UserInternal, roles: Dict[Role, List[Permission]] = Inject(role_config)
):
    # Populate the permissions hash from scratch
    user.permissions = {}

    for role in user.roles.keys():
        # Retrieve the permissions associated with the role
        permissions: Optional[List[Permission]] = roles.get(Role(role), None)

        if permissions is not None:
            # Apply all permissions granted by the role
            for permission in permissions:
                user.permissions[permission.value] = True
        else:
            # Remove invalid role
            del user.roles[role]


Dependency.register(synchronize_roles, synchronize_roles, scope=Scope.INSTANCED)


async def user(password: PasswordContext = Inject(password)):
    router = APIRouter()

    async def update_user_password_in_db(user_id: str, new_password: str) -> None:
        query = users.select().where(users.c.id == user_id)
        user_record = await database.fetch_one(query)

        if user_record is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user"
            )

        user = UserInternalPassword.from_orm(user_record)
        password_history = user.password_history
        new_hash = password.hash(new_password)

        if any(
            password.verify(new_password, old_hash) for old_hash in password_history
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reuse previous passwords",
            )

        password_history.append(new_hash)

        updated_user = UserInternalPassword(
            **user.dict(
                by_alias=True,
                exclude={"password", "password_history", "password_last_updated"},
            ),
            password=new_hash,
            password_history=password_history,
            password_last_updated=datetime.utcnow(),
        )

        query = users.update().where(users.c.id == updated_user.id)
        result = await database.execute(query, updated_user.dict())

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unable to update password",
            )

    @router.get(
        "",
        response_model=List[UserWithMetadata],
        dependencies=[Depends(require_permission(Permission.READ_USERS))],
    )
    async def get_users(skip: int = 0, limit: int = 10):
        query = users.select().limit(limit).offset(skip)
        all_users = await database.fetch_all(query)

        users_list = []
        for user in all_users:
            userWithMeta = UserWithMetadata.model_validate(
                User.model_validate(user).model_dump(), strict=False
            )

            query = user_login_tracking.select().where(
                user_login_tracking.c.user == user.id
            )
            login_tracking = await database.fetch_one(query)
            if login_tracking:
                login_tracking = UserLoginTracking.from_orm(login_tracking)
                userWithMeta.locked_until = login_tracking.locked_until

            query = user_security_settings.select().where(
                user_security_settings.c.user == user.id
            )
            security_settings = await database.fetch_one(query)
            if security_settings:
                security_settings = UserSecuritySettings.from_orm(security_settings)
                userWithMeta.otp_enabled = security_settings.otp_enabled

            users_list.append(userWithMeta)
        return users_list

    @router.post(
        "",
        response_model=User,
        dependencies=[Depends(require_permission(Permission.CREATE_USER))],
    )
    async def create_user(user: UserCreate):
        now = datetime.utcnow()

        try:
            create_user = UserPassword(
                **user.dict(by_alias=True, exclude={"password"}),
                created=now,
                last_modified=now,
                password=password.hash(user.password),
                password_last_updated=now,
            )
            await Dependency.resolve(synchronize_roles, create_user)

            query = users.insert()
            await database.execute(query, create_user.dict())
            query = users.select().where(users.c.id == create_user.id)
            created_user = await database.fetch_one(query)

            login_tracking = UserLoginTracking(
                user=create_user.id, attempts=0, last_attempt=datetime.utcnow()
            )
            query = user_login_tracking.insert()
            await database.execute(query, values=login_tracking.dict())

            sec_settings = UserSecuritySettings(user=create_user.id, otp_enabled=True)
            query = user_security_settings.insert()
            await database.execute(query, sec_settings.dict())

            return User.from_orm(created_user)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
            )

    @router.get(
        "/self",
        response_model=User,
        dependencies=[],
    )
    async def get_self(user: User = Depends(get_current_user)):
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No user found"
            )
        obj = user.__dict__
        return User.parse_obj(obj)

    @router.put(
        "/self/password",
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=[],
    )
    async def update_own_password(
        change: UserChangePassword, user: User = Depends(get_current_user)
    ):
        await update_user_password_in_db(user.id, change.password)

    @router.post("/forgot-password")
    async def forgot_password(username: str = ""):
        query = users.select().where(users.c.username == username)
        user = await database.fetch_one(query)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user"
            )
        user = UserInternalPassword.from_orm(user)

        # Create token to authenticate password reset
        payload = {"sub": user.id, "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(
            payload,
            Config.get(Settings.JWT_SECRET_KEY),
            algorithm=Config.get(Settings.JWT_ALGORITHM),
        )

        # Create and send email with password reset link
        body = (
            f"Password reset link: "
            f"{Config.get(Settings.FRONTEND_BASE_URL)}/#/login/set-password"
            f"?token={token}\n\n"
            "Do not share this link."
        )
        msg = MIMEText(body)
        msg["Subject"] = "VIMS Password Reset"
        msg["From"] = Config.get(Settings.MAIL_SERVER_ADDRESS)
        msg["To"] = user.email
        try:
            with smtplib.SMTP(
                Config.get(Settings.MAIL_SERVER_HOST),
                Config.get(Settings.MAIL_SERVER_PORT),
            ) as server:
                server.sendmail(
                    Config.get(Settings.MAIL_SERVER_ADDRESS),
                    [user.email],
                    msg.as_string(),
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unable to send password reset email",
            )

        return {}

    @router.post("/reset-password")
    async def reset_password(data: UserPasswordReset):
        print(data.token, data.password)
        try:
            payload = jwt.decode(
                data.token,
                Config.get(Settings.JWT_SECRET_KEY),
                algorithms=[Config.get(Settings.JWT_ALGORITHM)],
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token")

        user_id = payload.get("sub")
        await update_user_password_in_db(user_id, data.password)

        return {}

    @router.get(
        "/validate-username",
        dependencies=[Depends(require_permission(Permission.READ_USER))],
    )
    async def validate_username(username: str = ""):
        query = users.select().where(users.c.username == username)
        user = await database.fetch_one(query)

        return True if not user else False

    @router.get(
        "/login-tracking",
        summary="Get user login tracking",
        dependencies=[Depends(require_permission([Permission.ADMIN]))],
        response_model=List[UserLoginTracking],
    )
    async def get_login_tracking():
        query = user_login_tracking.select()
        result = await database.fetch_all(query)
        return result

    @router.get(
        "/unlock/{user_id}",
        summary="Unlock user",
        response_model=UserLoginTracking,
        dependencies=[Depends(require_permission([Permission.ADMIN]))],
    )
    async def unlock(user_id: str):
        query = user_login_tracking.select().where(
            user_login_tracking.c.user == user_id
        )
        login_tracking = await database.fetch_one(query)
        if login_tracking:
            login_tracking = UserLoginTracking.from_orm(login_tracking)
            login_tracking.attempts = 0
            login_tracking.locked_until = None
            query = user_login_tracking.update().where(
                user_login_tracking.c.user == user_id
            )
            await database.execute(query, values=login_tracking.dict())
            return login_tracking
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No user found"
            )

    @router.get(
        "/{user_id}",
        response_model=User,
        dependencies=[Depends(require_permission(Permission.READ_USER))],
    )
    async def get_user(user_id):
        query = users.select().where(users.c.id == user_id)
        user = await database.fetch_one(query)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No user found"
            )
        return User.from_orm(user)

    @router.put(
        "/{user_id}",
        response_model=User,
        dependencies=[Depends(require_permission(Permission.UPDATE_USER))],
    )
    async def update_user(user_id, update: UserUpdate):
        now = datetime.utcnow()

        query = users.select().where(users.c.id == user_id)
        current_user = await database.fetch_one(query)
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user"
            )

        update_user = UserInternal(
            **update.dict(by_alias=True, exclude={"password", "current_password"}),
            last_modified=now,
            id=user_id,
        )

        if update.password is not None and update.current_password is not None:
            current_user = UserPassword.from_orm(current_user)
            if not password.verify(update.current_password, current_user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
                )
            password_history = current_user.password_history
            new_hash = password.hash(update.password)
            if any(
                password.verify(update.password, old_hash)
                for old_hash in password_history
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot reuse previous passwords",
                )
            password_history.append(new_hash)
            update_user = UserInternalPassword(
                **update_user.dict(by_alias=True),
                password=new_hash,
                password_history=password_history,
                password_last_updated=datetime.utcnow(),
            )

        await Dependency.resolve(synchronize_roles, update_user)

        query = users.update().where(users.c.id == user_id)
        result = await database.execute(query, update_user.dict())

        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No user found"
            )
        query = users.select().where(users.c.id == user_id)
        user = await database.fetch_one(query)

        return User.from_orm(user)

    @router.put(
        "/{user_id}/password",
        dependencies=[Depends(require_permission(Permission.UPDATE_USER_PASSWORD))],
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def update_user_password(user_id, change: UserChangePassword):
        await update_user_password_in_db(user_id, change.password)
        return {}

    @router.delete(
        "/{user_id}",
        dependencies=[Depends(require_permission(Permission.DELETE_USER))],
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def delete_user(user_id):
        query = users.delete().where(users.c.id == user_id)
        result = await database.execute(query)
        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user found",
            )
        return {}

    return router
