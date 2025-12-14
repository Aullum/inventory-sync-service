from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.config import load_config
from app.infrastructure.http.client import build_httpx_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.config = load_config()
    app.state.http = build_httpx_client()

    try:
        yield
    finally:
        await app.state.http.aclose()


app = FastAPI(lifespan=lifespan)
