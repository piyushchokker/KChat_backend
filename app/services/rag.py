# RAG logic and orchestration will be implemented here
from app.workers.document_worker import process_job
from app.services.redis_queue import pop_from_queue
from app.utils.chunking import partition_pdf_sync,create_chunks_by_title_sync
from app.utils.ai_enhanced_docs import summarise_chunks
from langchain_core.documents import Document
from datetime import datetime
from io import BytesIO
import asyncio





async def rag():
    while True:
        print("Waiting for job...")

        try:
            job = await pop_from_queue()
        except Exception :
            print("check if redis server is running ")
            break
        # print("Job received:", job)
        print("Job type:", type(job))

        documents = []

        if job:
            print("Processing job")

            response, saved_filename = await process_job(job)
            print("Processed job")

            partition =  partition_pdf_sync(file=BytesIO(response))
            print("partition completed")

            chunks = create_chunks_by_title_sync(partition)
            print("chunk by title complete")

            processed_chunks = await summarise_chunks(chunks)
            print("summerisation complete")

            print(processed_chunks)

            # documents = []

            # base_metadata = {
            #     **job["records"],  # DB metadata
            #     "file_name": saved_filename,
            #     "processed_at": datetime.utcnow().isoformat()
            # }

            # for idx, chunk in enumerate(processed_chunks):

            #     # If your chunk is plain text
            #     if isinstance(chunk, str):
            #         page_content = chunk
            #         chunk_meta = {}
            #     else:
            #         # If chunk returns dict
            #         page_content = chunk["text"]
            #         chunk_meta = chunk.get("metadata", {})

            #     merged_metadata = {
            #         **base_metadata,
            #         **chunk_meta,
            #         "chunk_id": idx
            #     }

            #     doc = Document(
            #         page_content=page_content,
            #         metadata=merged_metadata
            #     )

            #     documents.append(doc)

            

    
            








            
            

            












        else:
            await asyncio.sleep(1)  # avoid busy loop


if __name__ == "__main__":  
    asyncio.run(rag())