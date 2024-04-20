from flask import Flask, request, session, render_template, jsonify, Response, redirect, url_for
from openai import OpenAI
from dotenv import load_dotenv
from os import getenv
import time

# Load the .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = getenv('FLASK_SECRET_KEY')

# Initialize the OpenAI API client
client = OpenAI()
client.api_key = getenv('OPENAI_API_KEY')

prompt_context = getenv('PROMPT_CONTEXT')

# Route to serve the webpage
@app.route("/")
def index():
    return render_template('index.html')

# Route to handle form submission and stream responses
@app.route("/submit", methods=["POST"])
def submit():
    if 'reset' in request.form:
        print("*** RESETTING MESSAGES ***")
        session['messages'] = []
        print("*** RESETTING CONVERSATION ***")
        session['conversation'] = []
        return redirect(url_for('index'))

    prompt = request.form['text']
    session['messages'].append({"role": "user", "content": prompt})
    if len(session['messages']) > 5:
        session['messages'].pop(0)
    session.modified = True

    return Response(generate_chat_stream(session['messages']), mimetype='text/event-stream')


def generate_chat_stream(msgs):
     chat_stream = client.chat.completions.create(
                messages=msgs,
                model="gpt-4-turbo",
                # Sets the sampling temperature to control randomness (0 makes output deterministic, 1 maximizes randomness, with 0.2 being more focused and less random).
                temperature=0.2,
                stream=True 
            )
     for message in chat_stream:
        if 'content' in message:
            yield f"data: {message['content']}\n\n"

if __name__ == "__main__":
    app.run(debug=True)
