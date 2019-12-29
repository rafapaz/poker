from poker import Poker
from user import User

class Room:
    def __init__(self):
        self.users = set()
        self.poker = Poker()
        self.in_game = False
        self.pause = False
        self.pause_time = 10
        self.pause_start = 0
        self.play_time = 30
        self.play_start = 0
    