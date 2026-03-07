# import json
# from typing import List
# from langchain_core.documents import Document
# from langchain_core.messages import HumanMessage
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv
# import os

# load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# # 1️⃣ Pure sync memory operation
# def separate_content_types(chunk):
#     """Analyze what types of content are in a chunk"""
#     content_data = {
#         "text": chunk.text,
#         "tables": [],
#         "images": [],
#         "types": ["text"],
#     }

#     if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "orig_elements"):
#         for element in chunk.metadata.orig_elements:
#             element_type = type(element).__name__

#             if element_type == "Table":
#                 content_data["types"].append("table")
#                 table_html = getattr(element.metadata, "text_as_html", element.text)
#                 content_data["tables"].append(table_html)

#             elif element_type == "Image":
#                 if hasattr(element, "metadata") and hasattr(
#                     element.metadata, "image_base64"
#                 ):
#                     content_data["types"].append("image")
#                     content_data["images"].append(
#                         element.metadata.image_base64
#                     )

#     content_data["types"] = list(set(content_data["types"]))
#     return content_data


# # 2️⃣ Fully synchronous OpenAI call
# def create_ai_enhanced_summary(text: str, tables: List[str], images: List[str]) -> str:
#     """Create AI-enhanced summary for mixed content synchronously"""
#     try:
#         llm = ChatOpenAI(
#             model="gpt-4o",
#             temperature=0,
#             api_key=OPENAI_API_KEY,
#         )

#         prompt_text = f"""
# You are creating a searchable description for document content retrieval.

# CONTENT TO ANALYZE:

# TEXT CONTENT:
# {text}
# """

#         if tables:
#             prompt_text += "\nTABLES:\n"
#             for i, table in enumerate(tables):
#                 prompt_text += f"\nTable {i+1}:\n{table}\n"

#         prompt_text += """
# YOUR TASK:
# Generate a comprehensive, searchable description that covers:
# 1. Key facts, numbers, and data points from text and tables
# 2. Main topics and concepts discussed
# 3. Questions this content could answer
# 4. Visual content analysis (charts, diagrams, patterns in images)
# 5. Alternative search terms users might use

# Make it detailed and searchable - prioritize findability over brevity.

# SEARCHABLE DESCRIPTION:
# """

#         message_content = [{"type": "text", "text": prompt_text}]

#         for image_base64 in images:
#             message_content.append(
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{image_base64}"
#                     },
#                 }
#             )

#         message = HumanMessage(content=message_content)

#         # 🔑 Using sync invoke instead of ainvoke
#         response = llm.invoke([message])

#         return response.content

#     except Exception as e:
#         print(f"❌ AI summary failed: {e}")
#         summary = f"{text[:300]}..."
#         if tables:
#             summary += f" [Contains {len(tables)} table(s)]"
#         if images:
#             summary += f" [Contains {len(images)} image(s)]"
#         return summary


# # 3️⃣ Fully synchronous chunk processor
# def summarise_chunks(chunks,record):
#     """Process all chunks synchronously"""
#     print("🧠 Processing chunks with AI Summaries...")

#     langchain_documents = []
#     total_chunks = len(chunks)

#     for i, chunk in enumerate(chunks):
#         current_chunk = i + 1
#         print(f"Processing chunk {current_chunk}/{total_chunks}")

#         content_data = separate_content_types(chunk)

#         if content_data["tables"] or content_data["images"]:
#             print("→ Creating AI summary for mixed content...")
#             enhanced_content = create_ai_enhanced_summary(
#                 content_data["text"],
#                 content_data["tables"],
#                 content_data["images"],
#             )
#             print("→ AI summary created")
#         else:
#             print("→ Using raw text (no tables/images)")
#             enhanced_content = content_data["text"]

#         doc = Document(
#             page_content=enhanced_content,
#             metadata={
#                 "original_content": json.dumps(
#                     {
#                         "raw_text": content_data["text"],
#                         "tables_html": content_data["tables"],
#                         "images_base64": content_data["images"],
#                     }),
#                 # File metadata
#                 "document_id": record["id"],
#                 "title": record["title"],
#                 "course": record["course"],
#                 "school": record["school"],
#                 "semester": record["semester"],
#                 "document_type": record["document_type"],
#                 "effective_from": record["effective_from"],
#                 "effective_till": record["effective_till"],
#                 "issuing_authority": record["issuing_authority"]          
#             },
#         )

#         langchain_documents.append(doc)

#     print(f"✅ Processed {len(langchain_documents)} chunks")
#     return langchain_documents


# --------------------------------------------------------------------------------------------

import json
import asyncio
from typing import List
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# 1️⃣ Sync (no need to make this async)
def separate_content_types(chunk):
    content_data = {
        "text": chunk.text,
        "tables": [],
        "images": [],
        "types": ["text"],
    }

    if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "orig_elements"):
        for element in chunk.metadata.orig_elements:
            element_type = type(element).__name__

            if element_type == "Table":
                content_data["types"].append("table")
                table_html = getattr(element.metadata, "text_as_html", element.text)
                content_data["tables"].append(table_html)

            elif element_type == "Image":
                if hasattr(element, "metadata") and hasattr(
                    element.metadata, "image_base64"
                ):
                    content_data["types"].append("image")
                    content_data["images"].append(
                        element.metadata.image_base64
                    )

    content_data["types"] = list(set(content_data["types"]))
    return content_data


# 2️⃣ Async OpenAI call
async def create_ai_enhanced_summary_async(
    llm: ChatOpenAI,
    text: str,
    tables: List[str],
    images: List[str],
) -> str:

    try:
        prompt_text = f"""
You are creating a searchable description for document content retrieval.

CONTENT TO ANALYZE:

TEXT CONTENT:
{text}
"""

        if tables:
            prompt_text += "\nTABLES:\n"
            for i, table in enumerate(tables):
                prompt_text += f"\nTable {i+1}:\n{table}\n"

        prompt_text += """
YOUR TASK:
Generate a comprehensive, searchable description that covers:
1. all the facts, all numbers, all codes  and all the data points in the doc
2. Main topics and concepts
3. Questions this content could answer
4. Visual content analysis
5. Alternative search terms

Make it detailed and searchable.

SEARCHABLE DESCRIPTION:
"""

        message_content = [{"type": "text", "text": prompt_text}]

        for image_base64 in images:
            message_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    },
                }
            )

        message = HumanMessage(content=message_content)

        # ✅ Async call
        response = await llm.ainvoke([message])

        return response.content

    except Exception as e:
        print(f"❌ AI summary failed: {e}")
        summary = f"{text[:300]}..."
        if tables:
            summary += f" [Contains {len(tables)} table(s)]"
        if images:
            summary += f" [Contains {len(images)} image(s)]"
        return summary


# 3️⃣ Process single chunk (async worker)
async def process_single_chunk(
    chunk,
    record,
    llm,
    semaphore,
    index,
    total,
):
    async with semaphore:
        print(f"Processing chunk {index}/{total}")

        content_data = separate_content_types(chunk)

        if content_data["tables"] or content_data["images"]:
            enhanced_content = await create_ai_enhanced_summary_async(
                llm,
                content_data["text"],
                content_data["tables"],
                content_data["images"],
            )
        else:
            enhanced_content = content_data["text"]

        return Document(
            page_content=enhanced_content,
            metadata={
                "original_content": json.dumps(
                    {
                        "raw_text": content_data["text"],
                        "tables_html": content_data["tables"],
                        "images_base64": content_data["images"],
                    }
                ),
                "document_id": record["id"],
                "title": record["title"],
                "course": record["course"],
                "school": record["school"],
                "semester": record["semester"],
                "document_type": record["document_type"],
                "effective_from": record["effective_from"],
                "effective_till": record["effective_till"],
                "issuing_authority": record["issuing_authority"],
            },
        )


# 4️⃣ Fully async chunk processor
async def summarise_chunks_async(chunks, record):

    print("🧠 Processing chunks asynchronously...")

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=OPENAI_API_KEY,
    )

    semaphore = asyncio.Semaphore(10)  # 🔒 limit concurrency (important)

    tasks = [
        process_single_chunk(
            chunk,
            record,
            llm,
            semaphore,
            i + 1,
            len(chunks),
        )
        for i, chunk in enumerate(chunks)
    ]

    langchain_documents = await asyncio.gather(*tasks)

    print(f"✅ Processed {len(langchain_documents)} chunks")
    return langchain_documents







