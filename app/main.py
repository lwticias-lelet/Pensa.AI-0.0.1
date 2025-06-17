import os
import shutil
from dotenv import load_dotenv
import gradio as gr
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.storage import StorageContext
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core import ServiceContext

from llama_index.indices.vector_store import VectorStoreIndex
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings

from app.llama_index_helper import get_index
from app.pdf_loader import load_pdfs_from_folder

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "mistralai/mistral-7b-instruct:free"
BASE_URL = "https://openrouter.ai/api/v1"

# Configura embeddings HuggingFace (via LangChain)
embed_model = HuggingFaceEmbeddings(model_name="hkunlp/instructor-base")

# Configura LLM via LangChain, usando OpenRouter com o modelo escolhido
llm = ChatOpenAI(
    openai_api_key=API_KEY,
    model_name=MODEL,
    base_url=BASE_URL,
    streaming=False,
)

# Cria o ServiceContext com llm e embedding (compatível com sua versão)
service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)

# Cria ou carrega o índice usando seu helper (ajuste seu helper para usar VectorStoreIndex)
index = get_index(service_context=service_context)

# Cria o chat engine com prompt customizado e serviço configurado
chat_engine = index.as_chat_engine(
    chat_mode="condense_question",
    service_context=service_context,
    system_prompt=(
        "Você é um assistente educacional. "
        "Ajude o aluno a resolver exercícios com passo a passo, sem fornecer respostas diretas. "
        "Dê explicações, dicas e resumos, incentivando o raciocínio do estudante."
    ),
    verbose=True,
)

def process_input(user_input):
    response = chat_engine.chat(user_input)
    return response.response

def handle_upload(files):
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    for file in files:
        dest = os.path.join(upload_dir, os.path.basename(file.name))
        shutil.copy(file.name, dest)

    new_docs = load_pdfs_from_folder(upload_dir)
    if new_docs:
        index.insert_documents(new_docs)
    return "Arquivos carregados e indexados com sucesso!"

with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Chatbot Educacional - Pensa.AI")

    chatbot = gr.Chatbot()
    user_input = gr.Textbox(placeholder="Digite sua pergunta...")

    with gr.Row():
        submit_btn = gr.Button("Enviar")
        clear_btn = gr.Button("Limpar chat")

    upload_box = gr.File(file_types=[".pdf"], file_count="multiple", label="Envie PDFs")
    upload_btn = gr.Button("Processar Arquivos")
    status = gr.Textbox(label="Status do upload", interactive=False)

    def respond(message, history):
        response = process_input(message)
        history = history + [(message, response)]
        return history, ""

    submit_btn.click(respond, [user_input, chatbot], [chatbot, user_input])
    clear_btn.click(lambda: [], None, chatbot)
    upload_btn.click(handle_upload, upload_box, status)

if __name__ == "__main__":
    demo.launch()
