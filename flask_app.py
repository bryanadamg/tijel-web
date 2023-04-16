from flask import Flask, render_template, request
import requests
from chatbot.bot import MeenaBot
from utils import authenticate
# import discord_bot

app = Flask(__name__)

authenticate.authOpenAI()
authenticate.authPinecone()
chatbot = MeenaBot('discord-msgs')

@app.route('/')
def hello_world():
    return render_template('body.html')


@app.route('/api/bot', methods=['POST'])
def bot_response():
    query = request.form['message']
    # chatbot = MeenaBot('discord-msgs')
    res = chatbot.ask(query)
    messages = [{'role': 'Human', 'message': query}, {'role': 'AI', 'message': res}]
    return render_template('chat_table.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')