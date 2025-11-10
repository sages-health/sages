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

# import uuid
#
# import pytest
#
# from httpx import AsyncClient
#
# from vims.app import base
# from vims.core import Dependency
#
# # AsyncClient is used as an alternative to TestClient
# # marks all tests as async
# pytestmark = pytest.mark.anyio
#
# HOST = "http://localhost:8081"
# AUTH_URL = "/auth"
# USER_URL = "/user"
# DATASOURCE = "/datasource"
#
# USERNAME = "admin"
# PASSWORD = "test"
#
#
# # Constructs the AsyncClient that contains all API endpoints
# @pytest.fixture(scope="session")
# async def client():
#     router = await Dependency.resolve(base)
#     client = AsyncClient(app=router, base_url=f"{HOST}/api/v1")
#     yield client
#
#
# # Token fixture retrieves access_token upon authentication
# @pytest.fixture(scope="session")
# async def token(client):
#     creds = {"username": USERNAME, "password": PASSWORD}
#     response = await client.post(f"{AUTH_URL}/login", data=creds)
#     data = response.json()
#     yield data["access_token"]
#
#
# # adds the authorization header containing the bearer token to the header
# @pytest.fixture(scope="session")
# def headers(token):
#     return {"Authorization": f"bearer {token}"}
#
#
# # returns correct login info
# @pytest.fixture(scope="session")
# def login_data():
#     return {"username": USERNAME, "password": PASSWORD}
#
#
# # generates a random uuid
# def rand_uuid():
#     return uuid.uuid4()
#
#
#
# # retrieves id of first user
# async def get_curr_user_id(client, headers):
#     response = await client.get("/user", headers=headers)
#     data = response.json()
#     return data[0]["_id"]
#
#
# # Tests the get datasources endpoint using the authorization header
# async def test_get_datasources(client, headers):
#     # TODO: datasources should be created or reliant upon the seeded data.
#     response = await client.get(DATASOURCE, headers=headers)
#     assert response.status_code == 200
#
#     data = response.json()
#     assert len(data) == 4
#
#
# # TODO: Add dataset CRUD tests
#
#
# # Tests login with correct credentials and logout
# async def test_login_logout(client, login_data):
#     response = await client.post(f"{AUTH_URL}/login", data=login_data)
#     assert response.status_code == 200
#
#     data = response.json()
#     response = await client.get(
#         f"{AUTH_URL}/logout",
#         headers={"Authorization": f"bearer {data['access_token']}"},
#     )
#     assert response.status_code == 202
#
#
# # Tests login with incorrect password
# async def test_password_invalid(client, login_data):
#     response = await client.post(
#         f"{AUTH_URL}/login",
#         data={"username": USERNAME, "password": "INCORRECT_PASSWORD"},
#     )
#     assert response.status_code == 401
#
#     data = response.json()
#     assert data["detail"] == "Invalid password"
#
#
# # Tests login with wrong email
# async def test_email_invalid(client):
#     response = await client.post(
#         f"{AUTH_URL}/login",
#         data={"username": "incorrect@user.name", "password": PASSWORD},
#     )
#     assert response.status_code == 404
#
#     data = response.json()
#     assert data["detail"] == "Invalid username"
#
#
# # Testing get all users
# async def test_get_all_users(client, headers):
#     response = await client.get(USER_URL, headers=headers)
#     assert response.status_code == 200
#
#     data = response.json()
#     assert data[0]["email"] == USERNAME
#     assert len(data) == 1
#
#
# # Tests invalid id
# async def test_get_user_invalid(client, headers):
#     random_id = get_random_id()
#     response = await client.get(f"{USER_URL}/{random_id}", headers=headers)
#     assert response.status_code == 404
#
#     data = response.json()
#     assert data["detail"] == "No user found"
#
#
# # Tests valid id (assumes there is always at least one user)
# async def test_get_user_valid(client, headers):
#     user_id = await get_curr_user_id(client, headers)
#     response = await client.get(f"{USER_URL}/{user_id}", headers=headers)
#     assert response.status_code == 200
#
#
# # Tests creation of a user and then deletion of that user
# async def test_create_user(client, headers):
#     new_user = {
#         "first_name": "Hello",
#         "last_name": "World",
#         "email": "worldh1@jhuapl.edu",
#         "password": "secretP@ssword1!",
#         "phone_number": "+1 (123) 456-7890",
#     }
#     response = await client.post(USER_URL, headers=headers, json=new_user)
#     assert response.status_code == 200
#
#     response = await client.get(USER_URL, headers=headers)
#     assert response.status_code == 200
#
#     data = response.json()
#     assert len(data) == 2
#
#     created_user = list(filter(lambda x: x["email"] == new_user["email"], data))[0]
#     response = await client.delete(f"{USER_URL}/{created_user['_id']}",
#     headers=headers)
#     assert response.status_code == 202
#
#     response = await client.get(USER_URL, headers=headers)
#     assert response.status_code == 200
#
#     data = response.json()
#     assert len(data) == 1
