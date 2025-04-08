from app.client import *
from dotenv import load_dotenv
from app.llm import *
from app.tts import *
from app.database import Database
import os
load_dotenv('.env')      
logger=logging.getLogger('discord.client')
llm=LLMService(model='gpt-3.5-turbo-0125',logger=logger)
intents=discord.Intents(messages=True,message_content=True)

tts=OpenAITTSService()
db=Database()
client=ShirokoClient(intents=intents,logger=logger,llm=llm,tts=tts,db=db)







client.run(os.getenv('DISCORD_TOKEN'))