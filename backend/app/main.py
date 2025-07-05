from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
from groq import Groq

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pensa.AI Backend",
    description="API para chatbot educacional",
    version="1.0.0"
)

# CORS CONFIGURADO
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

# Cliente Groq global
groq_client = None
sistema_inicializado = False

def verificar_groq_key():
    """Verifica se a GROQ_API_KEY está configurada"""
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        logger.error("❌ GROQ_API_KEY não encontrada!")
        return False
    
    logger.info("✅ GROQ_API_KEY encontrada")
    return True

def inicializar_groq():
    """Inicializa cliente Groq"""
    global groq_client, sistema_inicializado
    
    if sistema_inicializado:
        return True
    
    try:
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            return False
        
        groq_client = Groq(api_key=groq_key)
        
        # Teste rápido
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": "teste"}],
            max_tokens=10
        )
        
        sistema_inicializado = True
        logger.info("✅ Sistema Groq inicializado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Groq: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização do servidor"""
    logger.info("🚀 Iniciando Pensa.AI Backend...")
    
    if inicializar_groq():
        logger.info("✅ Backend pronto para uso!")
    else:
        logger.warning("⚠️ Backend iniciado com funcionalidade limitada")

@app.get("/")
async def root():
    return {
        "message": "Pensa.AI Backend está funcionando!", 
        "status": "online",
        "environment": "production" if os.getenv("RENDER") else "development"
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    status = {
        "status": "healthy",
        "groq_configured": verificar_groq_key(),
        "sistema_inicializado": sistema_inicializado,
        "environment": "production" if os.getenv("RENDER") else "development"
    }
    return status

def gerar_resposta_educacional(pergunta):
    """Gera resposta educacional usando Groq diretamente"""
    
    prompt = f"""
🎓 VOCÊ É O PENSA.AI - TUTOR EDUCACIONAL ESPECIALISTA

MISSÃO: Ensinar detalhadamente com exemplos, mas SEM dar o resultado final.

PERGUNTA DO ESTUDANTE: {pergunta}

RESPONDA SEGUINDO ESTA ESTRUTURA:

🎯 ANÁLISE: [Tipo de problema e conceitos envolvidos]

📚 CONCEITOS: [Definições claras e aplicações]

📐 FÓRMULAS: [Fórmulas necessárias com explicação]

🛠️ MÉTODO PASSO A PASSO:
Passo 1: [O que fazer]
Passo 2: [Próxima etapa]
[Continue conforme necessário]

📝 EXEMPLO RESOLVIDO:
[Problema similar com resolução completa]

🔄 VERIFICAÇÃO: [Como conferir resultados]

🎯 PARA SEU PROBLEMA: [Orientação específica SEM resolver]

IMPORTANTE: Dê exemplos COMPLETOS, mas NÃO resolva o problema específico perguntado.
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Erro no Groq: {e}")
        return f"""
🎓 RESPOSTA EDUCACIONAL PARA: {pergunta}

📚 METODOLOGIA GERAL:
1. Identifique o tipo de problema
2. Liste dados conhecidos e incógnitas  
3. Escolha a estratégia adequada
4. Execute passo a passo
5. Verifique o resultado

💡 DICA: Aplique esta metodologia sistemática no seu problema!
        """

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
        else:
            resposta = gerar_resposta_educacional(request.question)
        
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

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload de arquivo - funcionalidade básica"""
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")
    
    return {
        "filename": file.filename,
        "message": "Arquivo recebido! Funcionalidade de indexação será implementada em breve."
    }