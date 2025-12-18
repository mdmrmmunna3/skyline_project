# main.py
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import jose
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from skyline_apiserver.api.v1 import api_router
from skyline_apiserver.config import CONF, configure
from skyline_apiserver.context import RequestContext
from skyline_apiserver.core.security import (
    generate_profile_by_token,
    parse_access_token,
)
from skyline_apiserver.db import api as db_api
from skyline_apiserver.db import setup as db_setup
from skyline_apiserver.log import LOG, setup as log_setup
from skyline_apiserver.policy import setup as policies_setup
from skyline_apiserver.types import constants

PROJECT_NAME = "Skyline API"

# ---------------------------------------------------------
# LOAD CONFIG
# ---------------------------------------------------------
configure("skyline")

# ---------------------------------------------------------
# LIFESPAN
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log_setup(
        Path(CONF.default.log_dir).joinpath(CONF.default.log_file),
        debug=CONF.default.debug,
    )
    policies_setup()
    db_setup()
    LOG.info("Skyline API server started")
    yield
    LOG.info("Skyline API server stopped")

# ---------------------------------------------------------
# FASTAPI APP
# ---------------------------------------------------------
app = FastAPI(
    title=PROJECT_NAME,
    openapi_url=f"{constants.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8088",
        "http://127.0.0.1:8088",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# AUTH / TOKEN MIDDLEWARE
# ---------------------------------------------------------
@app.middleware("http")
async def validate_token(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    url_path = request.url.path
    LOG.debug(f"Request path: {url_path}")

    ignore_urls = [
        f"{constants.API_PREFIX}/login",
        f"{constants.API_PREFIX}/websso",
        "/static",
        "/docs",
        f"{constants.API_PREFIX}/openapi.json",
        "/favicon.ico",
        f"{constants.API_PREFIX}/sso",
        f"{constants.API_PREFIX}/config",
        f"{constants.API_PREFIX}/contrib/keystone_endpoints",
        # f"{constants.API_PREFIX}/contrib/domains",
        f"{constants.API_PREFIX}/contrib/regions",
    ]

    for ignore_url in ignore_urls:
        if url_path.startswith(ignore_url):
            return await call_next(request)

    if url_path.startswith(constants.API_PREFIX):
        token = request.cookies.get(CONF.default.session_name)

        if not token:
            return JSONResponse(
                {"message": "Unauthorized: missing token"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            try:
                db_api.purge_revoked_token()
            except Exception as e:
                LOG.warning(f"Skip revoked_token cleanup (DEV): {e}")

            parsed_token = parse_access_token(token)
            profile = generate_profile_by_token(parsed_token)

            request.state.context = RequestContext(
                user_id=profile.user.id,
                project_id=profile.project.id,
                project_name=profile.project.name,
                user_domain_id=profile.user.domain.id,
                project_domain_id=profile.project.domain.id,
                roles=[role.name for role in profile.roles],
                auth_token=profile.keystone_token,
            )

            request.state.profile = profile

            if 0 < profile.exp - time.time() < CONF.default.access_token_renew:
                profile.exp = int(time.time()) + CONF.default.access_token_expire
                request.state.token_needs_renewal = True
                request.state.new_token = profile.toJWTPayload()
                request.state.new_exp = str(profile.exp)

        except jose.exceptions.ExpiredSignatureError:
            return JSONResponse(
                {"message": "Unauthorized: token expired"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            LOG.exception(e)
            return JSONResponse(
                {"message": f"Unauthorized: {str(e)}"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    response = await call_next(request)

    if getattr(request.state, "token_needs_renewal", False):
        response.set_cookie(CONF.default.session_name, request.state.new_token)
        response.set_cookie(constants.TIME_EXPIRED_KEY, request.state.new_exp)

    return response

# ---------------------------------------------------------
# PROFILE ENDPOINT
# ---------------------------------------------------------
# @app.get(f"{constants.API_PREFIX}/profile")
# async def profile(request: Request):
#     profile = request.state.profile
#     return JSONResponse(
#     {
#         "keystone_token": profile.keystone_token,
#         "region": profile.region,
#         "exp": profile.exp,
#         "uuid": profile.uuid,

#         "project": {
#             "id": profile.project.id,
#             "name": profile.project.name,
#             "domain": {
#                 "id": profile.project.domain.id,
#                 "name": profile.project.domain.name,
#             },
#         },

#         "user": {
#             "id": profile.user.id,
#             "name": profile.user.name,
#             "domain": {
#                 "id": profile.user.domain.id,
#                 "name": profile.user.domain.name,
#             },
#         },

#         "roles": [
#             {
#                 "id": r.id,
#                 "name": r.name
#             } for r in profile.roles
#         ],

#         "keystone_token_exp": profile.keystone_token_exp,
#         "base_domains": profile.base_domains,

#         "endpoints": {
#             "nova": profile.endpoints.nova,
#             "neutron": profile.endpoints.neutron,
#             "keystone": profile.endpoints.keystone,
#             "glance": profile.endpoints.glance,
#         },

#         "projects": {
#             profile.project.id: {
#                 "name": profile.project.name,
#                 "enabled": profile.project.enabled,
#                 "domain_id": profile.project.domain.id,
#                 "description": profile.project.description,
#             }
#         },

#         "default_project_id": profile.project.id,
#         "version": profile.version,
#     }
# )


# # ---------------------------------------------------------
# # POLICIES ENDPOINT
# # ---------------------------------------------------------
# @app.get(f"{constants.API_PREFIX}/policies")
# async def policies(request: Request):
#     profile = request.state.profile
#     role_names = [r.name.lower() for r in profile.roles]
#     return JSONResponse(
#         {
#             "isAdmin": "admin" in role_names,
#             "canViewDashboard": "admin" in role_names or "member" in role_names,
#         }
#     )

# ---------------------------------------------------------
# OTHER ROUTES
# ---------------------------------------------------------
app.include_router(api_router, prefix=constants.API_PREFIX)
