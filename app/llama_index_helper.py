import os
from llama_index import VectorStoreIndex, StorageContext, SimpleDirectoryReader



def get_index(service_context):
    persist_dir = "index"
    uploads_dir = "data/uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    if not os.path.exists(persist_dir):
        # Carrega documentos da pasta uploads
        documents = SimpleDirectoryReader(uploads_dir).load_data()
        # Cria o índice usando o service_context
        index = VectorStoreIndex.from_documents(documents, service_context=service_context)
        # Persiste o índice no diretório
        index.storage_context.persist(persist_dir)
    else:
        # Carrega o índice do armazenamento persistido
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = VectorStoreIndex(storage_context=storage_context, service_context=service_context)

    return index
