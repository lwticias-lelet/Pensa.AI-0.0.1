from llama_index import SimpleDirectoryReader, VectorStoreIndex, StorageContext, ServiceContext
import os

INDEX_DIR = "backend/index"

_service_context = None
_index = None

def load_index():
    global _index, _service_context
    if os.path.exists(INDEX_DIR):
        _service_context = ServiceContext.from_defaults()
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
        _index = VectorStoreIndex.load_from_storage(storage_context, service_context=_service_context)
    else:
        # Caso não tenha índice, cria vazio
        _index = VectorStoreIndex([])

def get_response_from_query(question: str) -> str:
    global _index
    if _index is None:
        load_index()
    query_engine = _index.as_query_engine()
    response = query_engine.query(question)
    return str(response)
