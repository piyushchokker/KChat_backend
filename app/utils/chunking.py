# from unstructured.partition.pdf import partition_pdf
# from unstructured.chunking.title import chunk_by_title
# import asyncio

# async def partition_pdf_async(file: str):
#     """
#     Wraps the synchronous partition_pdf function in an async wrapper 
#     by running it in a separate background thread.
#     """
#     # asyncio.to_thread takes the function first, followed by its arguments
#     elements = await asyncio.to_thread(
#         partition_pdf,
#         file=file,
#         strategy="hi_res",
#         extract_images_in_pdf=True,
#         infer_table_structure=True,
#         extract_image_block_types=["Image"],
#         extract_image_block_to_payload=True,
#     )
    
#     return elements


# async def create_chunks_by_title_async(elements):
#     """Create intelligent chunks using title-based strategy asynchronously"""
#     print("🔨 Creating smart chunks...")
    
#     # asyncio.to_thread(function_name, *args, **kwargs)
#     chunks = await asyncio.to_thread(
#         chunk_by_title,
#         elements,                              # The parsed PDF elements from previous step
#         max_characters=3000,                   # Hard limit - never exceed 3000 characters per chunk
#         new_after_n_chars=2400,                # Try to start a new chunk after 2400 characters
#         combine_text_under_n_chars=500         # Merge tiny chunks under 500 chars with neighbors
#     )
    
#     return len(chunks),chunks




from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title



def partition_pdf_sync(file: str):
    """
    Synchronously runs the heavy PDF partitioning. 
    Safe to run in a dedicated background worker process.
    """
    # print(f"📄 Partitioning PDF: {file_path}")
    
    elements = partition_pdf(
        file=file,  # Use 'filename' for file paths in unstructured
        strategy="hi_res",
        extract_images_in_pdf=True,
        infer_table_structure=True,
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True,
    )
    
    return elements

def create_chunks_by_title_sync(elements):
    """Synchronously creates intelligent chunks."""
    print("🔨 Creating smart chunks...")
    
    chunks = chunk_by_title(
        elements,                               
        max_characters=3000,                   
        new_after_n_chars=2400,                
        combine_text_under_n_chars=500         
    )
    
    return len(chunks), chunks