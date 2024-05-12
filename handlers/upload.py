import shutil
from typing import List
from fastapi import FastAPI, File, UploadFile, APIRouter
import os
import uuid
import aiofiles
import aiofiles.os as aios
from os import getcwd
from fastapi.responses import FileResponse
upload_router = APIRouter()
read_router = APIRouter()

"""
@upload_router.post("/uploads")
async def upload_file(uploaded_file: UploadFile = File(...)):
    filename, file_extension = os.path.splitext(uploaded_file.filename)
    file_location = f"uploads/{uuid.uuid1()}{file_extension}"
    async with aiofiles.open(file_location, "wb") as out_file:
        content = await uploaded_file.read()  # async read
        await out_file.write(content)  # async write
    response_str = dict(status="success",file_name=file_location,original_name=uploaded_file.filename,web_url=file_location,type=file_extension )
    return response_str"""

@read_router.get("/uploads/{name_file}")
def download_file(name_file: str):
    return FileResponse(path=getcwd() + "/uploads/" + name_file, media_type='application/octet-stream', filename=name_file)
