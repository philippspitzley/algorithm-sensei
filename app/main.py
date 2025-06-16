from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api import limiter
from app.api.exceptions import add_exception_handlers
from app.initial_data import init

from .api.main import api_router
from .core.config import settings

# uncomment next two lines for sentry support
# import sentry_sdk
# sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    init()
    yield
    # Shutdown code if needed
    pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

app.state.limiter = limiter

# Initialize Logfire
logfire.configure(token=settings.LOGFIRE_TOKEN)
# logfire.instrument_fastapi(app, capture_headers=True)
# logfire.instrument_psycopg()

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,  # enables cookies for cross-origin requests
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

# add custom exception handlers for middleware like slowapi
add_exception_handlers(app)
