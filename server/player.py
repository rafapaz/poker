from card import Card

class Player:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.cards = []        
        
    def receive(self, card):
        self.cards.append(card)
        

    def __str__(self):
        ret = ''
        for c in self.cards:
            ret += str(c) + ' '
        return '{} -> {}'.format(self.name, ret)
    