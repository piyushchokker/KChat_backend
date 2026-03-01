from app.services.redis_queue import add_to_queue
from fastapi import APIRouter, Request
import os
import logging
# import uuid
# import json
from app.services.supabase_client import supabase
import httpx
import uuid
# import asyncio
# import aiofiles


router = APIRouter()

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)
http_client = httpx.AsyncClient(timeout=30.0)


@router.get("/")
def health_check():
    return {"status": "running"}

@router.post("/webhook/new-document")
async def new_document(request: Request):

    payload = await request.json()
    record = payload.get("record", {})

    file_path = record.get("storage_path")
    original_filename = record.get("file_name")
    file_unique_id = record.get("id")

    if not file_path or not original_filename:
        return {"status": "missing required fields"}

    # Only push minimal job data
    job_data = {
        "uuid":file_unique_id,
        "storage_path": file_path,
        "file_name": original_filename,
        "record": record
    }

    await add_to_queue(job_data)

    return {"status": "queued"}


# @router.post("/webhook/new-document")
# async def new_document(request: Request):

#     payload = await request.json()
#     record = payload.get("record", {})

#     bucket = "documents"
#     file_path = record.get("storage_path")
#     original_filename = record.get("file_name")

#     logging.info(f"Webhook received: payload={payload}")
#     logging.info(f"Parsed record: {record}")
#     logging.info(f"bucket={bucket}, file_path={file_path}, filename={original_filename}")

#     # Validate required fields
#     if not bucket or not file_path or not original_filename:
#         logging.error("Missing required fields in webhook payload.")
#         return {
#             "status": "missing required fields",
#             "payload": payload,
#             "record": record
#         }

#     # Generate signed URL
#     try:
#         # without asynic ->
#         # signed_url_resp = supabase.storage.from_(bucket).create_signed_url(file_path, 60)

#         signed_url_resp = await asyncio.to_thread(lambda: supabase.storage.from_(bucket).create_signed_url(file_path, 60))


#         signed_url = signed_url_resp.get("signedURL")

#         if not signed_url:
#             logging.error("Failed to generate signed URL.")
#             return {
#                 "status": "failed to generate signed url",
#                 "signed_url_resp": signed_url_resp
#             }

#     except Exception as e:
#         logging.error(f"Error generating signed URL: {str(e)}")
#         return {"status": f"error generating signed url: {str(e)}"}

#     # Download file
#     try:
#         response = await http_client.get(signed_url)

#         if response.status_code != 200:
#             logging.error(f"Download failed: {response.status_code}")
#             return {
#                 "status": f"download failed: {response.status_code}",
#                 "response_text": response.text
#             }

#         # Generate unique filename
#         file_unique_id = str(uuid.uuid4())
#         filename = f"{file_unique_id}_{original_filename}"
#         save_path = os.path.join(UPLOAD_FOLDER, filename)

#         # Save file locally with out async 
#         # with open(save_path, "wb") as f:
#         #     f.write(response.content)

#         # Save file locally with async 
#         async with aiofiles.open(save_path, "wb") as f:
#             await f.write(response.content)

#         logging.info(f"File saved at: {save_path}")


#         # Prepare metadata
#         metadata = {
#             "unique_id": file_unique_id,
#             "filename": filename,
#             "original_filename": original_filename,
#             "save_path": save_path,
#             "record": record,
#             "signed_url": signed_url
#         }


#         # Save metadata JSON

#         # metadata path
#         metadata_path = save_path + ".json"

#         # saving metadata with asyc
#         async with aiofiles.open(metadata_path, "w", encoding="utf-8") as meta_f:
#             await meta_f.write(json.dumps(metadata, ensure_ascii=False, indent=2))

#         # Add to Redis queue
#         await add_to_queue(metadata)

#         return {
#             "status": "file downloaded",
#             "unique_id": metadata.get("unique_id"),
#             "path": save_path
#         }

#     except Exception as e:
#         logging.error(f"Error downloading file: {str(e)}")
#         return {"status": f"error downloading file: {str(e)}"}