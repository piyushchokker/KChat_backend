from extractous import Extractor
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Tuple, Optional

def extract_and_split_pdf(
	pdf_path: str,
	chunk_size: int = 1000,
	chunk_overlap: int = 100,
	chunk_index: Optional[int] = None
) -> Tuple[List[str], dict]:

	try:
		extractor = Extractor()
		text, metadata = extractor.extract_file_to_string(pdf_path)
	except FileNotFoundError:
		raise FileNotFoundError(f"PDF file not found: {pdf_path}")
	except Exception as e:
		raise RuntimeError(f"Failed to extract text from PDF: {e}")

	try:
		text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
		texts = text_splitter.split_text(text)
	except Exception as e:
		raise RuntimeError(f"Failed to split text: {e}")

	if chunk_index is not None:
		if 0 <= chunk_index < len(texts):
			return [texts[chunk_index]], metadata
		else:
			raise IndexError(f"chunk_index {chunk_index} out of range (0-{len(texts)-1})")
	return texts