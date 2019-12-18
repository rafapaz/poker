from player import Player
from bot import Bot

class User:
    def __init__(self, name, websocket, bot=False):
        if bot:
            self.player = Bot(name, 1000)
        else:
            self.player = Player(name, 1000)
        self.websocket = websocket
        self.bot = bot