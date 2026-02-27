import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"), override=False)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
	raise ValueError("Supabase URL or Key not set in environment variables.")


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Document class to represent a document row
class Document:
	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			setattr(self, key, value)

	def __repr__(self):
		return f"<Document {self.__dict__}>"


# Function to fetch all documents with metadata from documents table
def fetch_all_documents():
	response = supabase.table("documents") \
		.select("*") \
		.order("created_at", desc=True) \
		.execute()
	if response.data:
		return [Document(**doc) for doc in response.data]
	return []


