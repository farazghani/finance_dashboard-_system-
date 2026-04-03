from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)