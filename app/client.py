import discord
import logging
from app.llm import LLMService
from app.rvc import *
from app.tts import *

class ShirokoClient(discord.Client):
    
    def __init__(self, *, intents,logger : logging.Logger,llm : LLMService,tts : OpenAITTSService, **options):
        super().__init__(intents=intents, **options)
        self.logger=logger
        self.llm=llm
        self.tts_service=tts
        
    
    async def on_ready(self):
        await self.change_presence(status=discord.Status.do_not_disturb,activity=discord.Game('Exercising'))
        self.logger.info('Shiroko Started')
        
    async def on_message(self,message : discord.Message):
        if message.author==self.user:
            return
        try:
            async with message.channel.typing():
                response=self.llm.prompt(message.content)
                self.logger.info(response)
                
                tts_audio=self.tts_service.tts(response)
                self.logger.info(tts_audio)
                async with AsyncRVCService(self.logger) as rvc:
                    await rvc.load_model()
                    character_audio, mime_type= await rvc.convert_file(tts_audio)
                    self.logger.info(character_audio)
                    audio_file=discord.File(fp=io.BytesIO(character_audio),filename='response.wav')
                    await message.channel.send(response,file=audio_file,tts=True)
        except Exception as e:
            sent_message=await message.channel.send('```ansi\n\u001b[0;30m\u001b[0;47 An unexpected error occored please contact support```')
            await sent_message.add_reaction('😵')
            self.logger.error(e)
            return