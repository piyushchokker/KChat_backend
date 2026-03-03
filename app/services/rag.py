# RAG logic and orchestration will be implemented here
from app.workers.document_worker import process_job
from app.services.redis_queue import pop_from_queue
from app.utils.chunking import partition_pdf_sync,create_chunks_by_title_sync
from app.utils.ai_enhanced_docs import summarise_chunks_async
# from langchain_core.documents import Document
# from datetime import datetime
import os
from io import BytesIO
from dotenv import load_dotenv
import asyncio
from app.services.text_extrator import extract_and_split_pdf
from app.services.qdrant_client import VectorStoreService
from langchain_openai import OpenAIEmbeddings

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

qudrant_client=VectorStoreService(collection_name="my-collection",embedding_model="text-embedding-3-large")


async def rag():
    print("RAG Worker Started...")

    while True:
        try:
            job = await pop_from_queue()
        except Exception as e:
            print("❌ Redis connection failed:", str(e))
            break

        if job:

            print("📦 Job received:", job)

            try:
                # 1️⃣ Process & Save file
                response,saved_filename = await process_job(job)
                print("✅ File processed:", saved_filename)

            except Exception as e:
                print("❌ Error processing job:", str(e))

            try:
                partition =  partition_pdf_sync(file=BytesIO(response))
                print("partition completed")
                print(f"No. of Partitions :{len(partition)}")

            except Exception :
                print("Error in partition completed")


            try :
                chunks = create_chunks_by_title_sync(partition)
                print(f"total chunks created : {len(chunks)}")

            except Exception:
                print("Error in chunk by title complete")
                
            processed_chunks = summarise_chunks_async(chunks,job["record"])


        # try :
        #     processed_chunks = summarise_chunks_async(chunks,job["record"])
        #     print(f"processed chunks : {len(processed_chunks)}")
        # except Exception :
        #     print("Error in summerisation complete")

        # try:
        #     qudrant_client.add_documents(processed_chunks)

        # except Exception:
        #     print("error while storing embedding ")
        
                




        else:
            await asyncio.sleep(1)  # avoid busy loop


if __name__ == "__main__":  
    asyncio.run(rag())