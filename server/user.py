from player import Player


class User:
    def __init__(self, name, websocket):
        self.player = Player(name, 1000)
        self.websocket = websocket       