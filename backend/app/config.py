import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Diretórios
INDEX_DIR = "backend/index"
UPLOAD_DIR = "backend/data/uploads"

# Configurações do servidor
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# CORS origins
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]