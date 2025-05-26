from typing import List
from fastapi import UploadFile
import tempfile
from core.celery.tasks import process_claim_chain


async def process_claim_files(files: List[UploadFile]) -> dict:
    task_ids = []
    for file in files:
        # Save uploaded file to a temp file
        
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(contents)
            temp_path = temp.name
        # Submit the chained tasks
        chain_result = process_claim_chain(temp_path)
        task = chain_result.apply_async()
        task_ids.append({
            "taskId":task.id,
            "finleName":file.filename
        })
    return task_ids
