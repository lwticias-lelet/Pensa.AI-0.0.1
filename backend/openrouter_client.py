import openai

openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = "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"

def call_model(prompt):
    response = openai.ChatCompletion.create(
        model="openrouter/llama3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']
