from flask import Flask, render_template, request, session, redirect, url_for
from openai import OpenAI
from dotenv import load_dotenv
from os import getenv

# Load the .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = getenv('FLASK_SECRET_KEY')

# Initialize the OpenAI API client
client = OpenAI()
client.api_key = getenv('OPENAI_API_KEY')

prompt_context = getenv('PROMPT_CONTEXT')

@app.route('/', methods=['GET', 'POST'])
def home():

    if 'messages' not in session:
        print("*** SETTING MESSAGES ***")
        session['messages'] = []
    if 'conversation' not in session:
        print("*** SETTING CONVERSATION ***")
        session['conversation'] = []
        
    if request.method == 'POST':
        if 'reset' in request.form:
            print("*** RESETTING MESSAGES ***")
            session['messages'] = []
            print("*** RESETTING CONVERSATION ***")
            session['conversation'] = []
            return redirect(url_for('home'))

        user_input = request.form.get('user_input')
        if user_input:
            prompt = prompt_context + user_input 

            # only send the last 5 messages to avoid hallucination 
            session['messages'].append({"role": "user", "content": prompt})
            if len(session['messages']) > 5:
                session['messages'].pop(0)

            chat_completion = client.chat.completions.create(
                messages=session['messages'],
                model="gpt-4-turbo",
                # Sets the sampling temperature to control randomness (0 makes output deterministic, 1 maximizes randomness, with 0.2 being more focused and less random).
                temperature=0.2,
                stream=False 
            )

            print(f"\nquestion: {user_input} -- answer: {chat_completion.choices[0].message.content[:20]}")

            session['conversation'].append({'question': user_input, 'answer': chat_completion.choices[0].message.content})
            print(f"session['conversation']: {session['conversation']}")
            session.modified = True

    return render_template('index.html', conversation=session.get('conversation', []))

if __name__ == '__main__':
    app.run(debug=True)
