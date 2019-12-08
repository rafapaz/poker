
class Card:
    def __init__(self, naipe, symbol, value):
        self.naipe = naipe
        self.symbol = symbol
        self.value = value
    
    def __str__(self):
        return '{}{}'.format(self.symbol, self.naipe[0])
