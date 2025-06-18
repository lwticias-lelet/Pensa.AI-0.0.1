from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.llama_index_helper import get_response_from_query
from backend.pdf_loader import save_upload_file

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajuste para produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Apenas arquivos PDF são aceitos."}
    path = await save_upload_file(file)
    # Aqui você pode atualizar seu índice (ex: reindexar)
    return {"filename": file.filename, "path": path}

@app.post("/chat")
async def chat(query: dict):
    question = query.get("question")
    if not question:
        return {"error": "Campo 'question' obrigatório"}
    response = get_response_from_query(question)
    return {"answer": response}
