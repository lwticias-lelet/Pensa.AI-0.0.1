from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import os
from .config import INDEX_DIR, OPENAI_API_KEY, UPLOAD_DIR

# Configurar o LlamaIndex
Settings.llm = OpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY)

_index = None

def load_index():
    """Carrega o índice existente ou cria um novo"""
    global _index
    
    if os.path.exists(INDEX_DIR) and os.listdir(INDEX_DIR):
        # Carrega índice existente
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
        _index = VectorStoreIndex.load_from_storage(storage_context)
        print("Índice carregado com sucesso!")
    else:
        # Cria novo índice vazio
        _index = VectorStoreIndex([])
        print("Novo índice criado!")

def update_index():
    """Atualiza o índice com documentos da pasta de upload"""
    global _index
    
    if not os.path.exists(UPLOAD_DIR) or not os.listdir(UPLOAD_DIR):
        print("Nenhum documento encontrado para indexar")
        return
    
    # Lê documentos da pasta de upload
    documents = SimpleDirectoryReader(UPLOAD_DIR).load_data()
    
    if _index is None:
        # Cria novo índice
        _index = VectorStoreIndex.from_documents(documents)
    else:
        # Atualiza índice existente
        for doc in documents:
            _index.insert(doc)
    
    # Persiste o índice
    os.makedirs(INDEX_DIR, exist_ok=True)
    _index.storage_context.persist(persist_dir=INDEX_DIR)
    print(f"Índice atualizado com {len(documents)} documentos!")

def get_response_from_query(question: str) -> str:
    """Obtém resposta para uma pergunta usando o índice"""
    global _index
    
    if _index is None:
        load_index()
    
    if _index is None:
        return "Nenhum documento foi indexado ainda. Por favor, faça upload de um PDF primeiro."
    
    try:
        query_engine = _index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )
        response = query_engine.query(question)
        return str(response)
    except Exception as e:
        return f"Erro ao processar pergunta: {str(e)}"

# Inicializa o índice ao importar o módulo
load_index()