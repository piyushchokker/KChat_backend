import asyncio
import os
import sys
import uuid
import json
import httpx
import aiofiles
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.services.redis_queue import pop_from_queue
from app.services.supabase_client import supabase


UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def process_job(job):

    bucket = "documents"
    file_path = job["storage_path"]
    original_filename = job["file_name"]

    # Generate signed URL (blocking → thread)
    signed_url_resp = await asyncio.to_thread(
        lambda: supabase.storage.from_(bucket).create_signed_url(file_path, 60)
    )

    signed_url = signed_url_resp.get("signedURL")
    if not signed_url:
        return

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(signed_url)

    if response.status_code != 200:
        return

    file_unique_id = str(uuid.uuid4())
    filename = f"{file_unique_id}_{original_filename}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(response.content)

    metadata = {
        "unique_id": file_unique_id,
        "filename": filename,
        "original_filename": original_filename,
        "save_path": save_path,
        "record": job["record"],
        "signed_url": signed_url
    }

    metadata_path = save_path + ".json"

    async with aiofiles.open(metadata_path, "w", encoding="utf-8") as meta_f:
        await meta_f.write(json.dumps(metadata, ensure_ascii=False, indent=2))

    print(f"Processed: {filename}")


async def worker():
    while True:
        job = await pop_from_queue()

        if job:
            await process_job(job)
        else:
            await asyncio.sleep(1)  # avoid busy loop


if __name__ == "__main__":  
    asyncio.run(worker())