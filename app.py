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

messages = []

@app.route('/', methods=['GET', 'POST'])
def home():
    global messages
    if request.method == 'POST':
        if 'reset' in request.form:
            messages = []
            session.pop('conversation', None)
            return redirect(url_for('home'))

        user_input = request.form.get('user_input')
        if user_input:
            prompt = user_input + "\n\nYou are a friendly CS tutor. If the user tries to ask for the solution to a coding problem, do not provide the answer in code. Instead suggest ways to approach the problem."

            # only send the last 5 messages to avoid hallucination
            messages.append({"role": "user", "content": prompt})
            if len(messages) > 5:
                messages.pop(0)

            chat_completion = client.chat.completions.create(
                messages=messages,
                model="gpt-4-turbo",
                # Sets the sampling temperature to control randomness (0 makes output deterministic, 1 maximizes randomness, with 0.2 being more focused and less random).
                temperature=0.2,
                stream=False 
            )
            if 'conversation' not in session:
                session['conversation'] = []
            session['conversation'].append({'question': user_input, 'answer': chat_completion.choices[0].message.content})


    
    return render_template('index.html', conversation=session.get('conversation', []))

if __name__ == '__main__':
    app.run(debug=True)
