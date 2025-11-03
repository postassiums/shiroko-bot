import logging
import sys

from app.bot import *
from dotenv import load_dotenv
from app.llm import *
from app.tts import *
from app.database import Database
import os
load_dotenv('.env')

logger=logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='static/logs/discord.log', encoding='utf-8', mode='w')
log_format='%(asctime)s:%(levelname)s:%(name)s: %(message)s'
handler.setFormatter(logging.Formatter(log_format))
std_out_handler= logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.addHandler(std_out_handler)


llm=LLMService(model='gpt-4.1-mini',logger=logger)
intents=discord.Intents(messages=True,message_content=True,voice_states=True,guild_messages=True,guilds=True)
tts=EdgeTTSService()
db=Database()
rvc_service=AsyncRVCService(logger=logger)
shiroko_voice_service=ShirokoVoiceService(tts_service=tts,rvc_service=rvc_service,logger=logger)
pdf_service=ShirokoPDFReader(shiroko_voice=shiroko_voice_service,logger=logger)
client=DiscordBot(intents=intents, logger=logger, llm=llm, tts=tts, db=db,shiroko_voice=shiroko_voice_service,pdf_service=pdf_service)







client.run(os.getenv('DISCORD_TOKEN'),log_handler=handler)