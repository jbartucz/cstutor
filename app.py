from openai import OpenAI
from dotenv import load_dotenv
from os import getenv
import gradio as gr

# Load the .env file
load_dotenv()

# Initialize the OpenAI API client
client = OpenAI()
client.api_key = getenv('OPENAI_API_KEY')

csci1133_prompt_context = getenv('PROMPT_CONTEXT')

def predict(message, history):
    history_openai_format = []
    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human })
        history_openai_format.append({"role": "assistant", "content":assistant})
    history_openai_format.append({"role": "user", "content": csci1133_prompt_context + " " + message})
    if len(history_openai_format) > 10: # five messages
         history_openai_format.pop(0)
         history_openai_format.pop(0)
  
    response = client.chat.completions.create(model='gpt-4-turbo',
    messages= history_openai_format,
    temperature=0.2,
    stream=True)

    partial_message = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
              partial_message = partial_message + chunk.choices[0].delta.content
              yield partial_message

gr.ChatInterface(predict).launch()