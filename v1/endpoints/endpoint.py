from fastapi import APIRouter, UploadFile, File, HTTPException
from core.utils.classify import process_claim_files
from typing import List
from celery.result import AsyncResult
from core.celery.celery import celery_app

router = APIRouter()

@router.post("/")
async def process_claim(files: List[UploadFile] = File(...)):
    result = await process_claim_files(files)
    return result

@router.get("/result/{task_id}")
def get_task_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.state,
        "result": None,
        "error": None,
        "traceback": None,
        "info": None
    }
    
    if task_result.state == 'PENDING':
        response["info"] = "Task is waiting for execution or unknown"
    elif task_result.state == 'SUCCESS':
        response["result"] = task_result.result
    elif task_result.state == 'FAILURE':
        response["error"] = str(task_result.result)
        response["traceback"] = task_result.traceback
    else:
        response["info"] = str(task_result.info)
    
    return response