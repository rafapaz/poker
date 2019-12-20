from card import Card

class Player:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.last_bet = 0
        self.cards = []        
        
    def receive(self, card):
        self.cards.append(card)

    def bet(self, value):
        if value > self.money:
            self.last_bet = self.money
            self.money = 0
            return self.last_bet
            
        self.money -= value
        self.last_bet = value
        return value

    def serialize(self, all=False):
        ret = dict()
        ret['name'] = self.name
        ret['money'] = self.money
        ret['last_bet'] = self.last_bet
        if all:
            ret['cards'] = [str(c) for c in self.cards]
        return ret

    def __str__(self):
        cards_str = ''
        for c in self.cards:
            cards_str += str(c) + ' '
        return '{} -> {} / {}'.format(self.name, cards_str, self.money)
    
    def __repr__(self):
        return str(self)
    