import os
from dotenv import load_dotenv

class Config:

    def __init__(self):
        load_dotenv()
        self.config = os.getenv

    def get(self, key, default=None):
        return os.environ.get(key, default)

    def set(self, key, value):
        os.environ[key] = value

    def unset(self, key):
        os.environ.pop(key, None)

