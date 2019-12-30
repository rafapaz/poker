from player import Player
from bot import Bot

class User:
    def __init__(self, name, money, websocket, bot=False):
        if bot:
            self.player = Bot(name, money)
        else:
            self.player = Player(name, money)
        self.websocket = websocket
        self.bot = bot