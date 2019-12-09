from card import Card

class Player:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.cards = []        
        
    def receive(self, card):
        self.cards.append(card)
    
    def serialize(self):
        ret = dict()
        ret['name'] = self.name
        ret['money'] = self.money
        return ret

    def __str__(self):
        ret = ''
        for c in self.cards:
            ret += str(c) + ' '
        return '{} -> {}'.format(self.name, ret)
    