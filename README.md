# Instalar virtualenv
pip install virtualenv

# Criar ambiente virtual
virtualenv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install fastapi uvicorn python-dotenv llama-index llama-index-llms-groq aiofiles python-multipart PyPDF2 sentence-transformers llama-index-embeddings-huggingface


# IMPORTANTE: Execute da raiz do projeto
uvicorn backend.app.main:app --reload -
- apos isso execute o front
