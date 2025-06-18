from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .llama_index_helper import get_response_from_query, update_index

from .pdf_loader import save_upload_file
from .config import CORS_ORIGINS
import uvicorn

app = FastAPI(
    title="Pensa.AI Backend",
    description="API para chatbot educacional com upload de PDFs",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.get("/")
async def root():
    return {"message": "Pensa.AI Backend está funcionando!"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload de arquivo PDF e atualização do índice"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")
    
    try:
        path = await save_upload_file(file)
        # Atualiza o índice com o novo documento
        update_index()
        return {"filename": file.filename, "path": path, "message": "Arquivo enviado e indexado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint para chat com o assistente"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Campo 'question' não pode estar vazio")
    
    try:
        response = get_response_from_query(request.question)
        return ChatResponse(answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)