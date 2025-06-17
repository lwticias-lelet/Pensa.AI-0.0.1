import os
from dotenv import load_dotenv
import gradio as gr
from llama_index.core import ServiceContext
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain_huggingface import HuggingFaceEmbeddings
from app.llama_index_helper import get_index
from app.pdf_loader import load_pdfs_from_folder
import shutil

load_dotenv()

# API OpenRouter
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "mistralai/mistral-7b-instruct:free"
BASE_URL = "https://openrouter.ai/api/v1"

# Embeddings
embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name="hkunlp/instructor-base")
)

# LLM + ServiceContext
llm = OpenAI(api_key=API_KEY, model=MODEL, base_url=BASE_URL)
service_context = ServiceContext.from_defaults(llm=llm)

# Index
index = get_index(embed_model)
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

    # Reindexar com novos documentos PDF
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
