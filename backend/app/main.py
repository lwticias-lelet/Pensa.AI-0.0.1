from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pensa.AI Backend",
    description="API para chatbot educacional com upload de PDFs",
    version="1.0.0"
)

# CORS CONFIGURADO PARA REDE - ACEITA QUALQUER ORIGEM
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

sistema_inicializado = False

def verificar_groq_key():
    """Verifica se a GROQ_API_KEY está configurada"""
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        logger.error("❌ GROQ_API_KEY não encontrada!")
        return False
    
    logger.info("✅ GROQ_API_KEY encontrada")
    return True

def inicializar_sistema():
    """Inicializa o sistema LlamaIndex"""
    global sistema_inicializado
    
    if sistema_inicializado:
        return True
    
    try:
        if not verificar_groq_key():
            return False
        
        from .llama_index_helper import setup_llama_index
        
        sucesso = setup_llama_index()
        if sucesso:
            sistema_inicializado = True
            logger.info("✅ Sistema inicializado com sucesso!")
        else:
            logger.error("❌ Falha na inicialização do sistema")
        
        return sucesso
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização do servidor"""
    logger.info("🚀 Iniciando Pensa.AI Backend...")
    logger.info("🌐 Servidor configurado para aceitar conexões de rede")
    
    # Criar diretórios necessários
    os.makedirs("backend/data/uploads", exist_ok=True)
    os.makedirs("backend/index", exist_ok=True)
    
    # Tentar inicializar o sistema
    if inicializar_sistema():
        logger.info("✅ Backend pronto para uso!")
    else:
        logger.warning("⚠️ Backend iniciado com funcionalidade limitada")

@app.get("/")
async def root():
    return {
        "message": "Pensa.AI Backend está funcionando!", 
        "status": "online",
        "network": "accessible"
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    status = {
        "status": "healthy",
        "groq_configured": verificar_groq_key(),
        "sistema_inicializado": sistema_inicializado,
        "cors": "enabled_for_all_origins"
    }
    return status

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload de arquivo PDF e atualização do índice"""
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")
    
    try:
        upload_dir = "backend/data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"📄 Arquivo salvo: {file.filename}")
        
        if sistema_inicializado:
            try:
                from .llama_index_helper import update_index
                update_index()
                logger.info("🔄 Índice atualizado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao atualizar índice: {e}")
        
        return {
            "filename": file.filename, 
            "path": file_path,
            "message": "Arquivo enviado e indexado com sucesso!"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint para chat com o assistente"""
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Campo 'question' não pode estar vazio")
    
    logger.info(f"💬 Pergunta recebida: {request.question[:50]}...")
    
    try:
        if not sistema_inicializado:
            resposta = f"""
🎓 SISTEMA PENSA.AI - MODO LIMITADO

⚠️ O sistema completo não está disponível no momento.

PARA SUA PERGUNTA: "{request.question}"

📚 ORIENTAÇÃO GERAL:
1. 🔍 IDENTIFIQUE o tipo de problema
2. 📖 ESTUDE os conceitos fundamentais  
3. 🧮 APLIQUE as fórmulas adequadas
4. ✅ VERIFIQUE o resultado

Configure a GROQ_API_KEY para funcionalidade completa!
            """
            return ChatResponse(answer=resposta)
        
        from .llama_index_helper import get_response_from_query
        
        resposta = get_response_from_query(request.question)
        logger.info("✅ Resposta gerada com sucesso")
        
        return ChatResponse(answer=resposta)
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar pergunta: {str(e)}")
        
        resposta = f"""
❌ ERRO NO PROCESSAMENTO

Pergunta: {request.question}

🎓 MÉTODO GERAL DE RESOLUÇÃO:
1. Leia e compreenda o problema
2. Identifique conceitos necessários  
3. Aplique fórmulas e métodos
4. Verifique o resultado

Erro técnico: {str(e)[:100]}
        """
        
        return ChatResponse(answer=resposta)

if __name__ == "__main__":
    import uvicorn
    # IMPORTANTE: host="0.0.0.0" permite acesso da rede
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)