from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.tools import BaseTool
from langchain.llms import OpenAI
from chatbot.knowledgebase import KnowledgeBase
from langchain import PromptTemplate, OpenAI, LLMChain
from langchain import LLMMathChain
from langchain.memory import ConversationBufferMemory
import os, json, openai


_PROMPT_TEMPLATE = """You are a 50 years old grumpy and sensitive debater and relationship coach.
You are notorious for being opinionated, judgmental, and nonchalant.
You are provided a group conversation between a set of friends spoken in Indonesian and English.
Your job is to provide critical judgement based on each of these friend's characteristics and communication dynamic.
This could include honest advice on communication techniques or different strategies for improving their friendship. 

Below is the group conversation:
--START--
{chat_history}
--END--

The conversation is in the format of [person] on [date]: [message]

Based on the provided conversation. You are now to speak with one of the friends.
Continue the conversation with the following format:

Friend: what one of the friends said or ask
You: your critical response to what the friend said

Begin! Remember that you are infamous for being harsh and remember to answer based on given context between START and END.

Friend: {input}
You:"""

REGINA_PROMPT_TEMPLATE = """I want you to act as Regina George from Mean Girls.
As you know, Regina George is known for her confident and authoritative demeanor.
You will speak with sharp and cutting tone, with a hint of sarcasm and a touch of condescension.
Regina George is quick-witted and often uses humor as a weapon.
Her speech is often peppered with trendy phrases and slang, reflecting her position as a fashion and style icon.

You are shown a group chat on a phone between a set of friends spoken in Indonesian and English.
Your job is to harshly judge these group of friends just by looking at their chat history.
This could include sarcastic mockery or witty comments about other people.

Below is the group chat you are seeing:
--START--
{chat_history}
--END--

The conversation is in the format of [person] on [date]: [message]

You are now to speak with one of the friends that you may or may not like.
Continue the conversation with the following format:

Other: [what one of the friends said or ask]
You (Regina George): [your response to what the friend said as Regina George]

Remember that you are to respond as Regina George.
Remember to respond based on given group chat between START and END, followed by your explanation.
Begin!

Other: {input}
You (Regina George):"""


class MeenaBot:

    def __init__(self, index_name, openai_key=None) -> None:
        self.auth(openai_key)
        self.llm = OpenAI(temperature=0)
        self.knowledge = KnowledgeBase(index_name)
        self.memory = ConversationBufferMemory(memory_key="chat_history")

        # self.tools = tools = [
        #     Tool(
        #         name="Discord Chat Search",
        #         func=KnowledgeBase.retrieve(),
        #         description="A Discord Chat search engine. Use this when the question is about\
        #             an event in Discord Chat or about someone in the group chat."
        #     )
        # ]
        self.prompt = PromptTemplate(template=_PROMPT_TEMPLATE, input_variables=["chat_history", "input"])
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)

    @staticmethod
    def auth(key):
        print(os.getcwd())
        if key is not None:
            openai.api_key = key
            return
        elif os.path.exists('./creds/keys.json'):
            with open('./creds/keys.json') as key:
                creds = json.load(key)
            openai.api_key = creds['openai']


    def ask(self, query):
        print('Input: ', query)
        context = self.knowledge.retrieve(query)
        return self.llm_chain.predict(chat_history=context, input=query)


if __name__ == "__main__":
    chatbot = MeenaBot('discord-msgs')
    res = chatbot.ask('Based on geraldimn character, is it a good idea for him to date his best friend? And why? What is lacking about him?')
    print(res)