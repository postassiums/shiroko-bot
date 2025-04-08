
import os
import typing as t
from openai import OpenAI,Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from math import ceil
from pathlib import Path
from enum import Enum

import httpx
import edge_tts
from dotenv import load_dotenv

import tempfile
import abc
import io
from app.llm import ChatGPT
from logging import Logger
    

OpenAITTSModels=t.Literal['tts-1','tts-1-hd']   
OpenAITTSVoices=t.Literal['alloy', 'ash', 'coral', 'echo', 'fable', 'onyx', 'nova', 'sage', 'shimmer']
AudioFormat=t.Literal['mp3', 'opus', 'aac', 'wav']
         

class OpenAITTSService(ChatGPT):


        
  
    
    
    
    def __init__(self,voice: OpenAITTSVoices='nova', model : OpenAITTSModels='tts-1',STREAM_CHUNK: t.Optional[int]=1024,speed : t.Optional[int]=1,format: t.Optional[AudioFormat]='mp3',logger =Logger):
        self.voice=voice
        if not(self._voice_exists()):
            raise RuntimeError(f'The specific voice {self.voice} does not exists')
        
        super().__init__(model=model,logger=logger)
            
        self.STREAM_CHUNK=STREAM_CHUNK
        self.speed=speed
        self.audio_format=format
        self.logger=logger
        
    def get_mime_type(self):
        mime_type_dict={
            "mp3": 'mpeg',
            'opus': 'ogg'
        }
        return f'audio/{self.audio_format}' if self.audio_format not in mime_type_dict.keys() else f'audio/{mime_type_dict.get(self.audio_format)}'
        
    def get_audio_format(self):
        return self.audio_format

    def _voice_exists(self):
        return self.voice in t.get_args(OpenAITTSVoices)

   
    

    
    
 
    
    def tts(self,content : str):
        response=self.client.audio.speech.create(model=self.model,voice=self.voice,input=content,speed=self.speed,response_format=self.audio_format)
        audio=bytes()
        for chunk in response.iter_bytes(self.STREAM_CHUNK):
            audio+=chunk
        return audio
    

