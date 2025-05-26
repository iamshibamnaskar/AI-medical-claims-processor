from fastapi import APIRouter
from v1.endpoints.endpoint import router as claim_router

api_router = APIRouter()
api_router.include_router(claim_router, prefix="/process", tags=["Claim Processor"])