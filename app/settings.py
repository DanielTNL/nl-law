import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION = os.getenv("COLLECTION", "bwb_articles")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-large")
GEN_MODEL = os.getenv("GEN_MODEL", "gpt-4o")
BACKEND_CORS_ORIGINS = os.getenv("BACKEND_CORS_ORIGINS", "*").split(",")
PORT = int(os.getenv("PORT", "8080"))
