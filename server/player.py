from card import Card

class Player:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.cards = []        
        
    def receive(self, card):
        self.cards.append(card)

    def bet(self, value):
        self.money -= value
        return value

    def serialize(self):
        ret = dict()
        ret['name'] = self.name
        ret['money'] = self.money
        return ret

    def __str__(self):
        cards_str = ''
        for c in self.cards:
            cards_str += str(c) + ' '
        return '{} -> {} / {}'.format(self.name, cards_str, self.money)
    
    def __repr__(self):
        return str(self)
    