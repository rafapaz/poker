import random
from player import Player

class Bot(Player):
    def play(self, table_cards, table_value):
        value = 0
        if table_value == 0:
            choices = ['fold', 'check', 'raise']
        else:
            choices = ['fold', 'call', 'raise']

        action = random.choice(choices)
        if action == 'raise':
            value = int(random.random() * (self.money/2))
            
        return action, value