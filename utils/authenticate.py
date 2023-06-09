import os, json
import openai
import pinecone

PATH = f'{os.getcwd()}/creds/keys.json'

def authOpenAI():
    if os.path.exists(PATH):
        print('key file found')
        with open(PATH) as key:
            creds = json.load(key)
            openai.api_key = creds['openai']
            print('Authenticated OpenAI')
    return

def authPinecone():
    if os.path.exists(PATH):
        with open(PATH) as key:
            creds = json.load(key)
            pinecone.init(
                api_key=creds['pinecone'],
                environment=creds['pinecone_env']
            )
    return