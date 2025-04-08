from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, Indexed, init_beanie
import os
from app.schema import *

class Database:

    def __init__(self):

        ENV_KEYS=['DB_HOST','DB_PASSWORD','DB_PORT','DB_USER']
        self.DB_HOST=os.getenv('DB_HOST')
        self.DB_PASSWORD=os.getenv('DB_PASSWORD')
        self.DB_PORT=os.getenv('DB_PORT')
        self.DB_USER=os.getenv('DB_USER')
        self.URL=f'mongodb://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}'

    async def init(self):
        # Create Motor client
        client = AsyncIOMotorClient(self.URL)

        # Init beanie with the Product document class
        await init_beanie(database=client.shiroko, document_models=[Conversation])

