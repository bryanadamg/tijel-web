from langchain.document_loaders import UnstructuredWordDocumentLoader
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
import openai
import pinecone
import uuid, json
from time import sleep
import os

EMBED_MODEL = "text-embedding-ada-002"


class KnowledgeBase:
    
    def __init__(self, index_name, fname=None, documents=None, encoder='cl100k_base') -> None:
        # self.auth()
        if fname is None or documents is None:
            # index is expected to be ready
            print('Looking for index: ', index_name)
            self.index = self.connectPinecone(index_name)
            return
        self.tokenizer = tiktoken.get_encoding(encoder)
        self.save_path = f'./data/{fname}.jsonl'
        self.documents = documents
        self.index = self.connectPinecone(index_name)


    @staticmethod
    def auth():
        if os.path.exists('./creds/keys.json'):
            with open('./creds/keys.json') as key:
                creds = json.load(key)
            openai.api_key = creds['openai']
            pinecone.init(
                api_key=creds['pinecone'],
                environment=creds['pinecone_env']
            )


    # create the length function
    def tiktoken_len(self, text):
        tokens = self.tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)
    

    def chunkDocs(self, docs):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=20,  # number of tokens overlap between chunks
            length_function=self.tiktoken_len,
            separators=['\n\n', '\n']
        )

        documents = []
        for i, doc in enumerate(tqdm(docs)):
            chunks = text_splitter.split_text(doc.page_content)
            url = doc.metadata['source'].replace('docs/', './data/')
            uid = uuid.uuid4()
            for i, chunk in enumerate(chunks):
                documents.append({
                    'id': f'{uid}-{i}',
                    'text': chunk,
                    'source': url
                })

        # if os.path.exists(self.save_path):
        #     pass
        with open(self.save_path, 'w') as f:
            for doc in documents:
                f.write(json.dumps(doc) + '\n')

        return documents
    

    def upsertDocs(self, index_name):
        index = pinecone.Index(index_name)
        self.documents = self.chunkDocs(self.documents)
        batch_size = 100  # how many embeddings we create and insert at once
        print('Document Length: ', len(self.documents))

        for i in tqdm(range(0, len(self.documents), batch_size)):
            i_end = min(len(self.documents), i+batch_size)
            meta_batch = self.documents[i:i_end]
            ids_batch = [x['id'] for x in meta_batch]
            # get texts to encode
            texts = [x['text'] for x in meta_batch]
            try:
                res = openai.Embedding.create(input=texts, engine=EMBED_MODEL)
            except Exception as e:
                print('Embedding Failed: ', e)
                done = False
                while not done:
                    sleep(3)
                    try:
                        res = openai.Embedding.create(input=texts, engine=EMBED_MODEL)
                        done = True
                    except:
                        pass
            embeds = [record['embedding'] for record in res['data']]
            # cleanup metadata
            meta_batch = [{
                'text': x['text'],
                'source': x['source']
            } for x in meta_batch]
            to_upsert = list(zip(ids_batch, embeds, meta_batch))
            # upsert to Pinecone
            index.upsert(vectors=to_upsert)

        return index



    def connectPinecone(self, index_name):
        pinecone.init(
            api_key=os.getenv("PINECONE_KEY"),
            environment=os.getenv("PINECONE_ENV")
        )
        if index_name not in pinecone.list_indexes():
            print('Creating New Index...')
            pinecone.create_index(
                index_name,
                dimension=1536,
                metric='cosine',
                # metadata_config={'indexed': ['channel_id', 'published']}
            )
            return self.upsertDocs(index_name)
        index = pinecone.Index(index_name)
        print('Pinecone Index status: ', index.describe_index_stats())
        return index
    

    def customPrompt(self, context, query):
        prompt = f"""Answer the question based on the context below. If the
            question cannot be answered using the information provided answer
            with "I don't know".

            Context: {context}

            Question: {query}

            Answer: """
        return prompt
    

    def retrieve(self, query):
        res = openai.Embedding.create(input=[query], engine=EMBED_MODEL)
        xq = res['data'][0]['embedding']

        res = self.index.query(xq, top_k=5, include_metadata=True)
        contexts = [x['metadata']['text'] for x in res['matches']]
        return '\n'.join(contexts)

    def ask(self, query):

        res = openai.Embedding.create(input=[query], engine=EMBED_MODEL)
        xq = res['data'][0]['embedding']

        res = self.index.query(xq, top_k=2, include_metadata=True)
        contexts = [x['metadata']['text'] for x in res['matches']]

        res = openai.Completion.create(
            engine='text-davinci-003',
            prompt=self.customPrompt('\n'.join(contexts), query),
            temperature=0,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        print(res['choices'][0]['text'].strip())




if __name__ == "__main__":
    from discord_loader import DiscordChatLoader

    loader = DiscordChatLoader('./data/general.json')
    docs = loader.load()

    knowledge = KnowledgeBase('discord-chunks', 'discord-msgs', docs)
    # knowledge.upsertDocs('discord-msgs')
    print(knowledge.ask('What are important points to be remembered by a Project Manager?'))
    # print(docs[0])



