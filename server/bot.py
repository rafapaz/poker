from player import Player

class Bot(Player):
    def play(self, table_cards, table_value):
        return 'check', 0