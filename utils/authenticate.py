import os, json
import openai
import pinecone

def authOpenAI():
    print(f'{os.getcwd()}/creds/keys.json')
    if os.path.exists(f'{os.getcwd()}/creds/keys.json'):
        with open('./creds/keys.json') as key:
            creds = json.load(key)
        openai.api_key = creds['openai']
    return

def authPinecone():
    if os.path.exists(f'{os.getcwd()}/creds/keys.json'):
        with open('./creds/keys.json') as key:
            creds = json.load(key)
            pinecone.init(
                api_key=creds['pinecone'],
                environment=creds['pinecone_env']
            )
    return