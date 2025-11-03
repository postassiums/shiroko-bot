import io

import discord
import logging
from app.llm import LLMService
from app.pdf import ShirokoPDFReader
from app.rvc import *
from app.tts import *
from app.database import Database
from app.schema import *
from datetime import timedelta
from discord.ext import commands
import traceback
from PyPDF2 import PdfReader
import json
import uuid
from app.debug import bk,start_debug_session
from app.voice import ShirokoVoiceService


class DiscordBot(commands.Bot):
    PDF_FILE_READ_LIMIT=10
    
    def __init__(self, *, intents, logger : logging.Logger, llm : LLMService,
                 db : Database, shiroko_voice : ShirokoVoiceService,pdf_service : ShirokoPDFReader, **options):
        super().__init__(intents=intents,command_prefix='$', **options)
        self.logger=logger
        self.llm=llm
        self.shiroko_voice=shiroko_voice
        self.pdf_service=pdf_service
        self.db=db
     
    async def _send_pdf_result(self,result : tuple[str,bytes] ,interaction : discord.Interaction):
        for file_name, audio in result:
            message_content = f'FILE: {file_name} \n'
            audio_file=discord.File(fp=io.BytesIO(audio),filename=f'{uuid.uuid4()}.wav')
            await interaction.followup.send(file=audio_file, content=message_content, ephemeral=True)


    async def _convert_pdf_attachments_to_audio(self, messages_with_attachemnts,interaction : discord.Interaction):
        for message in messages_with_attachemnts:
            attachments = message.attachments
            message_content = f"TRANSCRIBING LAST {attachments.__len__()} FILES:"
            sent_message = await interaction.response.send_message(content=message_content, ephemeral=True)
            result = await self.pdf_service.pdfs_to_audio(attachments)
            # await Conversation.create_chatbot_conversation(sent_message,f"PAGE {page}:\n" + to_be_read_text)
            await self._send_pdf_result(result, interaction)

    async def register_tree_commands(self):

        @self.tree.command(description='PING bot')
        async def ping(interaction : discord.Interaction):
            await interaction.response.send_message('PONG!')

        @self.tree.command(description='Clear all bot conversations you had with it ( ⚠️ DANGEROUS! ⚠️ )')
        async def clear(interaction : discord.Interaction):
            async with interaction.user.typing():
                await Conversation.find(Conversation.user_id==interaction.user.id).delete_many()
                await interaction.response.send_message('Conversations deleted')

        @self.tree.command(description="Make Shiroko join your voice channel")
        async def join(interaction: discord.Interaction):
                # Check if user is in a voice channel

            has_voice=hasattr(interaction.user,'voice')
            is_in_voice_channel=isinstance(interaction.user,User) and has_voice  and  \
                    interaction.user.voice is not None and interaction.user.voice.channel is not None
            if not(is_in_voice_channel):
                await interaction.response.send_message(
                    "❌ You must be in a voice channel first!",
                    ephemeral=True
                )
                return
            
                

            channel = interaction.user.voice.channel
            voice_client = interaction.guild.voice_client

            # Case 1: Bot already in user's channel
            if voice_client and voice_client.channel == channel:
                await interaction.response.send_message(
                    "🤖 I'm already in your voice channel!", 
                    ephemeral=True
                )
                return

            # Case 2: Bot in different channel
            if voice_client:
                await voice_client.move_to(channel)
                await interaction.response.send_message(f"🚚 Moved to **{channel.name}**!")
                return

            # Case 3: Bot not connected
            try:
                await channel.connect()
                await interaction.response.send_message(f"🎧 Joined **{channel.name}**!")
            except discord.ClientException as e:
                await interaction.response.send_message(
                    f"⚠️ Failed to join: {e}", 
                    #ephemeral=True
                )

        @self.tree.command(description="Make Shiroko leave the voice channel")
        async def leave(interaction: discord.Interaction):
            if interaction.guild is not None and interaction.guild.voice_client:
                await interaction.guild.voice_client.disconnect()
                await interaction.response.send_message("Disconnected.")
                return
            
            await interaction.response.send_message("I'm not in a voice channel.")


        @self.tree.command(description='Transcribe PDF Files',name='read')
        async def read_pdf(interaction : discord.Interaction):
            await interaction.response.defer(ephemeral=True,thinking=True)
            last_messages = [m async for m in interaction.channel.history(limit=self.PDF_FILE_READ_LIMIT)]
            messages_with_attachments=ShirokoPDFReader.filter_messages_with_attachments(last_messages)
            if messages_with_attachments.__len__()==0:
                
                await interaction.followup.send(content='No PDF Files were provied')
                return
            attachments=ShirokoPDFReader.get_attachments_from_messages(messages_with_attachments)
            attachments=ShirokoPDFReader.filter_pdf_attachments(attachments)
            try:
                async with interaction.channel.typing():

                    message_content=f"TRANSCRIBING LAST {attachments.__len__()} FILES:"
                    result=await self.pdf_service.pdfs_to_audio(attachments)
                    #await Conversation.create_chatbot_conversation(sent_message,f"PAGE {page}:\n" + to_be_read_text)
                    await self._send_pdf_result(result,interaction)
                    await interaction.followup.send(content='Finished to read PDF file',ephemeral=True)

            except Exception as e:
                self.logger.critical(e,exc_info=True)
                await interaction.followup.send(content="Failed to read the provided PDF files",ephemeral=True)





                
            



        await self.tree.sync()



    async def on_ready(self):
        await self.register_tree_commands()
        await self.change_presence(status=discord.Status.do_not_disturb,activity=discord.Game('Exercising'))
        try:
            await self.db.init()
            self.logger.info('Conected to the database')
            async with AsyncRVCService(self.logger) as rvc:
                    await rvc.load_model('shiroko')
                    self.logger.info('Loaded RVC model')
        except Exception as e:
            self.logger.critical(e)
            self.logger.critical(f'Failed to conect to the databases : {self.db.URL}')
            exit(1)
        self.logger.info('Shiroko Started')

    async def _take_action(self):
        function_calls=await self.llm.prompt(await Conversation.all().to_list())
        if function_calls is None or function_calls.name.__contains__('nothing'):
            return False
        function_arguments=json.loads(function_calls.arguments)
        content=function_arguments.get('content')
        if content is None:
            return False
        character_audio=await self.shiroko_voice.talk(content)
        audio_file=discord.File(fp=io.BytesIO(character_audio),filename=f'{uuid.uuid4()}.wav')
        chosen_function=getattr(self,function_calls.name)
        self.logger.info(f'Calling {chosen_function.__name__} with arguments {function_arguments}')
        return await chosen_function(**function_arguments,audio=audio_file)


    async def _handle_error(self,exception : Exception,message : discord.Message):
        sent_message=await message.reply('```An unexpected error occured please contact support```')
        await sent_message.add_reaction('😵')
        self.logger.error(traceback.print_exception(exception))

    async def _reply(self,message_id : int,channel_id : int,content: str,audio : discord.File):
        target_channel=self.get_channel(channel_id)
        if target_channel is None:
            self.logger.error(f'Channel {channel_id} not found')
            return
        target_message=target_channel.get_partial_message(message_id)
        if target_message is None:
            self.logger.error(f'Message {message_id} not found')
            return
        self.logger.info(target_message)
        sent_message=await target_message.reply(content,file=audio)
        return (content,sent_message)


    async def _send_message(self,channel_id : int, content : str,audio : discord.File):
        target_channel=self.get_channel(channel_id)
        if target_channel is None:
            self.logger.error(f'Channel {channel_id} not found')
            return
        sent_message=await target_channel.send(content,file=audio)
        return (content,sent_message)


    
    async def on_message(self,message : discord.Message):
        if message.author==self.user or message.content.strip().__len__()==0:
            return
        try:
            await Conversation.create(message)
            async with message.channel.typing():
                bot_response=await self._take_action()
                if bot_response==False:
                    self.logger.info('Bot chose to do nothing')
                    return
                content,sent_message=bot_response
                await Conversation.create_chatbot_conversation(sent_message,content)
                
               
            
            
        except Exception as e:
            await self._handle_error(e,message)
            return