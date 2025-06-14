import gradio as gr
from app.handlers import process_input

def create_ui():
    with gr.Blocks(css="static/style.css") as demo:
        gr.Markdown("# 🤖 Pensa.AI - Aprenda com Inteligência")
        user_input = gr.Textbox(label="Digite sua dúvida ou tema")
        output = gr.Textbox(label="Resposta guiada")
        btn = gr.Button("Enviar")
        btn.click(fn=process_input, inputs=user_input, outputs=output)
    return demo
