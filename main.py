from fastapi import FastAPI
from v1.api import api_router

app = FastAPI(title="Health Claim Processor")

app.include_router(api_router, prefix="/v1")