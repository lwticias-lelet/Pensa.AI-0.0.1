import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
    Document
)
from llama_index.llms.groq import Groq
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Diretórios usados
PERSIST_DIR = "backend/index"
UPLOADS_DIR = "backend/data/uploads"

# Variáveis globais
_index = None
_initialized = False

# SISTEMA DE PROMPTS EDUCACIONAIS
EDUCATIONAL_SYSTEM_PROMPT = """
Você é o Pensa.AI, um tutor educacional especializado. Sua missão é ENSINAR, não dar respostas prontas.

PRINCÍPIOS FUNDAMENTAIS:
1. 🎓 NUNCA forneça respostas diretas
2. 📚 SEMPRE ensine o processo de raciocínio
3. 🔍 Guie o estudante a descobrir por si mesmo
4. 📝 Use métodos pedagógicos eficazes
5. 🎯 Foque apenas em educação e aprendizado

ESTRUTURA OBRIGATÓRIA DE RESPOSTA:
🤔 ANÁLISE: [O que a pergunta está pedindo]
📋 CONCEITOS: [Conhecimentos necessários]
🛣️ MÉTODO: [Passo a passo para resolver]
💡 DICAS: [Como pensar sobre o problema]
🎯 PRÓXIMOS PASSOS: [O que o estudante deve fazer]

IMPORTANTE: Ensine o PROCESSO, não a resposta final!
"""

def setup_llama_index():
    """Configura o LlamaIndex com foco educacional"""
    global _initialized
    
    if _initialized:
        return True
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("⚠️  GROQ_API_KEY não encontrada no arquivo .env")
        return False
    
    try:
        # Configurar LLM com comportamento educacional
        llm = Groq(
            model="mixtral-8x7b-32768",
            api_key=groq_api_key,
            system_prompt=EDUCATIONAL_SYSTEM_PROMPT  # Prompt educacional global
        )
        
        Settings.llm = llm
        _initialized = True
        print("✅ Sistema educacional Pensa.AI configurado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar sistema: {str(e)}")
        return False

def ensure_directories():
    """Garante que os diretórios necessários existem"""
    try:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        os.makedirs(PERSIST_DIR, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Erro ao criar diretórios: {str(e)}")
        return False

def create_educational_index():
    """Cria um índice com conteúdo educacional inicial"""
    try:
        educational_content = Document(
            text="""
            Bem-vindo ao Pensa.AI - Seu Tutor Educacional!
            
            Como funciona o aprendizado eficaz:
            
            1. QUESTIONAMENTO: Sempre questione o que você está aprendendo
            2. CONEXÕES: Conecte novos conceitos com conhecimentos anteriores
            3. PRÁTICA: Aplique o que aprendeu em diferentes contextos
            4. REFLEXÃO: Pense sobre o processo de aprendizado
            5. ENSINO: Ensine outros para consolidar o conhecimento
            
            Métodos de estudo eficazes:
            - Técnica Pomodoro para gestão de tempo
            - Mapas mentais para organizar informações
            - Flashcards para memorização
            - Método Feynman para compreensão profunda
            - Prática espaçada para retenção
            
            Áreas de conhecimento que posso te ajudar:
            - Matemática: álgebra, geometria, cálculo
            - Ciências: física, química, biologia
            - Humanas: história, geografia, filosofia
            - Linguagens: português, literatura, redação
            - Tecnologia: programação, algoritmos
            - Métodos de estudo e aprendizado
            """
        )
        
        index = VectorStoreIndex.from_documents([educational_content])
        print("✅ Índice educacional básico criado")
        return index
        
    except Exception as e:
        print(f"❌ Erro ao criar índice educacional: {str(e)}")
        return None

def build_index_from_documents():
    """Constrói índice a partir dos documentos educacionais"""
    try:
        ensure_directories()
        
        # Verificar PDFs educacionais
        pdf_files = []
        if os.path.exists(UPLOADS_DIR):
            pdf_files = [f for f in os.listdir(UPLOADS_DIR) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print("📚 Criando base de conhecimento educacional inicial")
            return create_educational_index()
        
        print(f"📖 Carregando {len(pdf_files)} material(is) educacional(is)...")
        
        # Carregar documentos educacionais
        documents = SimpleDirectoryReader(UPLOADS_DIR).load_data()
        
        if not documents:
            return create_educational_index()
        
        # Adicionar contexto educacional aos documentos
        for doc in documents:
            doc.text = f"""
MATERIAL EDUCACIONAL:
{doc.text}

INSTRUÇÕES PARA O TUTOR:
- Use este material para ensinar, não para dar respostas diretas
- Guie o estudante através do processo de aprendizado
- Faça perguntas que estimulem o pensamento crítico
- Conecte este conteúdo com outros conhecimentos
"""
        
        # Adicionar documento educacional básico
        documents.append(create_educational_index().docstore.docs[list(create_educational_index().docstore.docs.keys())[0]])
        
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        
        print(f"💾 Base educacional criada com {len(documents)} recursos")
        return index
        
    except Exception as e:
        print(f"❌ Erro ao construir base educacional: {str(e)}")
        return create_educational_index()

def get_index():
    """Retorna o índice educacional"""
    global _index
    
    if _index is not None:
        return _index
    
    try:
        if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
            print("📚 Carregando base de conhecimento educacional...")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            _index = VectorStoreIndex.load_from_storage(storage_context)
            print("✅ Base educacional carregada!")
            return _index
        else:
            print("🆕 Criando nova base educacional...")
            _index = build_index_from_documents()
            return _index
            
    except Exception as e:
        print(f"❌ Erro ao carregar base: {str(e)}")
        _index = create_educational_index()
        return _index

def is_educational_query(query: str) -> bool:
    """Verifica se a pergunta é educacional"""
    non_educational = [
        'tempo', 'clima', 'notícia', 'fofoca', 'receita culinária',
        'comprar', 'vender', 'preço', 'dinheiro', 'investimento',
        'relacionamento amoroso', 'namoro', 'celebridade'
    ]
    
    query_lower = query.lower()
    return not any(keyword in query_lower for keyword in non_educational)

def format_educational_prompt(query: str, context: str) -> str:
    """Formata o prompt para resposta educacional"""
    return f"""
{EDUCATIONAL_SYSTEM_PROMPT}

CONTEXTO EDUCACIONAL DISPONÍVEL:
{context}

PERGUNTA DO ESTUDANTE: {query}

RESPONDA SEGUINDO RIGOROSAMENTE A ESTRUTURA:
🤔 ANÁLISE: [Analise o que o estudante quer aprender]
📋 CONCEITOS: [Que conhecimentos são necessários]
🛣️ MÉTODO: [Passo a passo para chegar na resposta]
💡 DICAS: [Como pensar sobre este problema]
🎯 PRÓXIMOS PASSOS: [O que o estudante deve fazer para praticar]

LEMBRE-SE: ENSINE o processo, NÃO dê a resposta pronta!
"""

def get_response_from_query(query: str) -> str:
    """Gera resposta educacional para a pergunta"""
    try:
        print(f"🎓 Pergunta educacional recebida: {query}")
        
        # Verificar se é pergunta educacional
        if not is_educational_query(query):
            return """
🎓 Como tutor educacional, só posso ajudar com questões de aprendizado! 

📚 Posso te ensinar sobre:
• Matemática, Física, Química, Biologia
• História, Geografia, Literatura  
• Programação e Tecnologia
• Métodos de estudo e aprendizado
• E muito mais!

🤔 Que tal reformular sua pergunta focando no que você gostaria de APRENDER?
            """
        
        # Configurar sistema
        if not setup_llama_index():
            return "❌ Sistema educacional não disponível. Verifique a configuração da API."
        
        # Obter base de conhecimento
        index = get_index()
        if index is None:
            return "❌ Base de conhecimento educacional não disponível."
        
        # Configurar engine educacional
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact",
            system_prompt=EDUCATIONAL_SYSTEM_PROMPT
        )
        
        # Gerar resposta educacional
        educational_prompt = format_educational_prompt(query, "")
        response = query_engine.query(educational_prompt)
        
        result = str(response)
        
        # Verificar se a resposta segue padrão educacional
        if not any(emoji in result for emoji in ['🤔', '📋', '🛣️', '💡', '🎯']):
            result = f"""
🤔 ANÁLISE: Você quer aprender sobre: {query}

📋 CONCEITOS: Para responder isso, você precisa entender os fundamentos do tema.

🛣️ MÉTODO: 
1. Primeiro, identifique os conceitos-chave
2. Pesquise em fontes confiáveis
3. Conecte com conhecimentos anteriores
4. Pratique com exemplos

💡 DICAS: Sempre questione o "porquê" por trás dos conceitos!

🎯 PRÓXIMOS PASSOS: Que tal começar pesquisando os termos principais desta pergunta?

{result}
            """
        
        print(f"✅ Resposta educacional gerada")
        return result
        
    except Exception as e:
        return f"""
❌ Erro no sistema educacional: {str(e)}

🎓 Mas posso te dar uma dica geral: para aprender qualquer coisa:
1. 🤔 Questione o que você quer saber
2. 📚 Pesquise em fontes confiáveis  
3. 🛣️ Divida em passos menores
4. 💡 Pratique com exemplos
5. 🎯 Ensine para alguém!
        """

def update_index():
    """Atualiza a base educacional"""
    global _index
    
    try:
        print("🔄 Atualizando base educacional...")
        
        if not setup_llama_index():
            return False
        
        _index = None
        _index = build_index_from_documents()
        
        if _index:
            print("✅ Base educacional atualizada!")
            return True
        else:
            print("❌ Falha ao atualizar base")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao atualizar: {str(e)}")
        return False

# Inicialização
print("🎓 Inicializando Pensa.AI - Sistema Educacional...")
if setup_llama_index():
    ensure_directories()
    get_index()
    print("✅ Sistema educacional Pensa.AI pronto para ensinar!")
else:
    print("⚠️  Sistema iniciado com limitações")