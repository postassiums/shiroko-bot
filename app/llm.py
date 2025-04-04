
import os
from openai import OpenAI
import random
import typing as t
import base64
OpenAIModels=t.Literal['gpt-4', 'gpt-3.5-turbo']
OpenAITTSModels=t.Literal['tts-1','tts-1-hd']   
OpenAITTSVoices=t.Literal['alloy', 'ash', 'coral', 'echo', 'fable', 'onyx', 'nova', 'sage', 'shimmer']
AudioFormat=t.Literal['mp3', 'opus', 'aac', 'wav']
class ChatGPT():
    
    def __init__(self,model : OpenAIModels | OpenAITTSModels='gpt-4o-audio-preview-2024-12-17'):
        
        self.API_KEY=os.getenv('OPENAI_API_KEY')
        self.model=model
        self.client=OpenAI(api_key=self.API_KEY)
        
        if self.model_exists()==False:
            raise RuntimeError(f'The fallowing model: {self.model} does not exists on OPENAI')
        
    def model_exists(self):
        models_response=self.client.models.list().data
        result=list(filter(lambda item: item.id==self.model,models_response))
        return result.__len__()>0
        
    def __repr__(self):
        return f'Model: {self.model} \n API_KEY: {self.API_KEY}'

class LLMService(ChatGPT):
    
    __instance__=None
    
    def __new__(cls,*args,**kwargs) :
        if cls.__instance__ is None:
            cls.__instance__=super().__new__(cls)
            # cls.__instance__._set_system_prompt()
            
        
        
        return cls.__instance__
    
    
    # def _set_system_prompt(self):
    #     with open('static/shiroko_prompt.md','r') as f:
    #         self.system_prompt=f.read()
    
    

    
    def prompt(self,user_prompt : str):
        completion= self.client.chat.completions.create(model=self.model,audio={'format': 'wav','voice': 'coral'},modalities=['text'],messages=[
            {"role": "developer","content":"You are Sunnaokami Shiroko from the game Blue Archieve"},
            {"role": "user","content": user_prompt}
        ])

        choices=completion.choices
        chonsen_index=random.randint(0,choices.__len__()-1)
        message=choices[chonsen_index].message
        return message.content

