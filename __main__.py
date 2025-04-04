from app.client import *
from dotenv import load_dotenv
from app.llm import *
from app.tts import *
import os
load_dotenv('.env')      
logger=logging.getLogger('discord.client')
llm=LLMService('gpt-3.5-turbo-0125')
intents=discord.Intents(messages=True)
tts=OpenAITTSService()
client=ShirokoClient(intents=intents,logger=logger,llm=llm,tts=tts)
client.run(os.getenv('DISCORD_TOKEN'))