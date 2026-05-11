<<<<<<< HEAD
import uuid

from fastapi import FastAPI,Request

from app.api.lifespan import lifespan
from app.api.routers.query_router import query_router
from app.core.context import request_id_context_var

# @asynccontextmanager
# def lifespan ():

app = FastAPI(lifespan=lifespan)

app.include_router(query_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = uuid.uuid4()
    request_id_context_var.set(request_id)
    response = await call_next(request)
=======
import uuid

from fastapi import FastAPI,Request

from app.api.lifespan import lifespan
from app.api.routers.query_router import query_router
from app.core.context import request_id_context_var

# @asynccontextmanager
# def lifespan ():

app = FastAPI(lifespan=lifespan)

app.include_router(query_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = uuid.uuid4()
    request_id_context_var.set(request_id)
    response = await call_next(request)
>>>>>>> 508f862c7b3e6c80529d6c31d82af3c6592ddf40
    return response