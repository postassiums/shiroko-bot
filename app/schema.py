from beanie import Document, Indexed, init_beanie
from pydantic import Field
import typing as t
from datetime import datetime,timezone
from uuid import *

Roles=t.Literal['developer','user','assistant']

class Conversation(Document):
    role: Roles='developer'
    content: str
    user_id : int


    

class CreateConversation(Conversation):
    created_at : datetime=Field(default_factory=lambda :datetime.now(tz=timezone.utc))

class UpdateConversation(Conversation):
    updated_at : datetime=Field(default_factory=lambda : datetime.now(tz=timezone.utc))



