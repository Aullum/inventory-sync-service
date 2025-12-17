from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.config import load_config
from app.infrastructure.http.client import build_httpx_client
from app.infrastructure.marketplaces.factory import MarketplaceAdapterFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.config = load_config()
    app.state.http = build_httpx_client()

    app.state.marketplace_factory = MarketplaceAdapterFactory(
        http=app.state.http,
        app_config=app.state.config,
    )

    try:
        yield
    finally:
        await app.state.http.aclose()


app = FastAPI(lifespan=lifespan)
