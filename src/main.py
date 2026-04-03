from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api import api_router
from src.core.exceptions import register_exception_handlers
from src.db.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)
app.include_router(api_router)
