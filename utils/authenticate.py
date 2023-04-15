import os, json
import openai

def authOpenAI():
    if os.path.exists('./creds/keys.json'):
        with open('./creds/keys.json') as key:
            creds = json.load(key)
    openai.api_key = creds['openai']
    return

def authPinecone():
    if os.path.exists('./creds/keys.json'):
        with open('./creds/keys.json') as key:
            creds = json.load(key)
    return