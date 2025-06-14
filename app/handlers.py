from backend.openrouter_client import call_model
from backend.prompts import wrap_prompt

def process_input(question):
    prompt = wrap_prompt(question)
    return call_model(prompt)
