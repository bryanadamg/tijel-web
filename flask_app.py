from flask import Flask, render_template, request
import requests
from chatbot.bot import MeenaBot
from utils import authenticate
# import discord_bot
import os

app = Flask(__name__)

# authenticate.authOpenAI()
# authenticate.authPinecone()
# chatbot = MeenaBot('discord-msgs')

@app.route('/')
def hello_world():

    envs = str(os.environ)

    return '<br>'.join(envs.split(','))



if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')