import os
from dotenv import load_dotenv
import gradio as gr

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    LangchainEmbedding
)
from langchain.embeddings import HuggingFaceInstructEmbeddings
from llama_index.llms.openai import OpenAI
from llama_index.core import ServiceContext

load_dotenv()

# Configurações da API
API_KEY = os.getenv("OPENROUTER_API_KEY")  # coloque sua chave no .env
MODEL = "mistralai/mistral-7b-instruct:free"
BASE_URL = "https://openrouter.ai/api/v1"

# Cria o embed_model local
embed_model = LangchainEmbedding(
    HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-base")
)

# Cria ou carrega índice LlamaIndex
if not os.path.exists("index"):
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    index.storage_context.persist("index")
else:
    storage_context = StorageContext.from_defaults(persist_dir="index")
    index = load_index_from_storage(storage_context)

# Configura o LLM OpenRouter
llm = OpenAI(api_key=API_KEY, model=MODEL, base_url=BASE_URL)
service_context = ServiceContext.from_defaults(llm=llm)

# Cria motor de chat
chat_engine = index.as_chat_engine(
    chat_mode="condense_question",
    service_context=service_context,
    system_prompt=(
        "Você é um assistente educacional. "
        "Ajude o aluno a resolver exercícios com passo a passo, sem fornecer respostas diretas. "
        "Forneça explicações, dicas e resumos, incentivando o raciocínio do estudante. "
        "Nunca forneça a resposta direta, apenas dicas e como chegar à resposta. "
        "Foque em temas relacionados a educação."
    ),
    verbose=True,
)

def process_input(user_input):
    response = chat_engine.chat(user_input)
    return response.response

def create_ui():
    with gr.Blocks() as ui:
        gr.Markdown("# Chatbot Educacional - Pensa.AI")

        chatbot = gr.Chatbot()
        user_input = gr.Textbox(placeholder="Digite sua pergunta aqui...")
        clear_btn = gr.Button("Limpar")

        def respond(message, chat_history):
            answer = process_input(message)
            chat_history = chat_history + [(message, answer)]
            return chat_history, ""

        user_input.submit(respond, [user_input, chatbot], [chatbot, user_input])
        clear_btn.click(lambda: [], None, chatbot)

    return ui

if __name__ == "__main__":
    ui = create_ui()
    ui.launch()
