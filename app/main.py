import gradio as gr
from app.ui import create_ui

def main():
    demo = create_ui()
    demo.launch()

if __name__ == "__main__":
    main()
