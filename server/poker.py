
from collections import Counter
from deck import Deck
from player import Player

class Poker:
    def __init__(self, players=None):        
        self.players = players if players is not None else set()
        self.fold = set()
        self.score = ['High Card', 'Pair', 'Two pairs', 'Three of a kind', 'Straight', 'Flush', 
                        'Full House', 'Four of a Kind', 'Straight Flush', 'Royal Flush'] # 0-9
            
    def start_game(self):
        self.deck = Deck()
        self.table_cards = []
        self.table_money = 0
        self.players = self.players and self.fold
        self.fold = set()

    def register_player(self, player):
        self.players.add(player)
    
    def unregister_player(self, player):
        self.players.remove(player)

    def reveal_card(self):
        self.table_cards.append(self.deck.give())
    
    def deliver(self):
        for p in self.players:
            p.cards = []
            p.receive(self.deck.give())
            p.receive(self.deck.give())
        
    def get_money(self, value):
        self.table_money += value

    def fold_player(self, player):
        self.fold.add(player)
        self.players.remove(player)

    def winner(self):
        best = None
        score = -1
        cod_score = -1
        
        for p in self.players:
            cs = self.get_score(p)
            value_player_cards = max([c.value for c in p.cards])
            total_score = cs + value_player_cards
            if total_score > score:
                score = total_score
                cod_score = cs
                best = p

        best.money += self.table_money
        self.table_money = 0
        return best, self.score[cod_score]

    def get_score(self, player):
        total_cards = self.table_cards + player.cards
                
        if self.is_royalflush(total_cards):
            return 9
        if self.is_straightflush(total_cards):
            return 8
        if self.is_fourofakind(total_cards):
            return 7
        if self.is_fullhouse(total_cards):
            return 6
        if self.is_flush(total_cards):
            return 5
        if self.is_straight(total_cards):
            return 4
        if self.is_threeofakind(total_cards):
            return 3
        if self.is_twopair(total_cards):
            return 2
        if self.is_pair(total_cards):
            return 1

        return 0

    def is_royalflush(self, cards):
        cards_str = [c.symbol+c.naipe[0] for c in cards]
        symbols = ['10', 'J', 'Q', 'K', 'A']
        
        i = 0
        for n in self.deck.naipes:
            for s in symbols:
                if s+n[0] in cards_str:
                    i += 1
            if i == 5:
                break
            i = 0            
        
        return True if i == 5 else False

    def is_straightflush(self, cards):        
        seq = 0
        for n in self.deck.naipes:
            subset = sorted([c for c in cards if c.naipe == n], key=lambda c: c.value)            
            for i in range(1, len(subset)):
                if subset[i].value - subset[i-1].value == 1:
                    seq += 1
                else:
                    seq = 0
                if seq >= 4:
                    break
            if seq >= 4:
                break
            seq = 0
        
        return True if seq >= 4 else False

    def is_fourofakind(self, cards):
        symbols = [c.symbol for c in cards]
        histogram = Counter(symbols)
        for k,v in histogram.items():
            if v == 4:
                return True
        
        return False

    def is_fullhouse(self, cards):
        symbols = [c.symbol for c in cards]
        histogram = Counter(symbols)
        has_3 = False
        has_2 = False
        for k,v in histogram.items():
            if v == 3:
                has_3 = True
            elif v == 2:
                has_2 = True
        
        return True if (has_3 and has_2) else False
    
    def is_flush(self, cards):
        naipes = [c.naipe for c in cards]
        histogram = Counter(naipes)
        for k,v in histogram.items():
            if v == 5:
                return True
        
        return False

    def is_straight(self, cards):
        cards = sorted(cards, key=lambda c: c.value)
        seq = 0
        for i in range(1, len(cards)):
            if cards[i].value - cards[i-1].value == 1:
                seq += 1
            else:
                seq = 0
            if seq >= 4:
                break
        
        return True if seq >= 4 else False
    
    def is_threeofakind(self, cards):
        symbols = [c.symbol for c in cards]
        histogram = Counter(symbols)
        for k,v in histogram.items():
            if v == 3:
                return True
        
        return False
    
    def is_twopair(self, cards):
        symbols = [c.symbol for c in cards]
        histogram = Counter(symbols)
        i = 0
        for k,v in histogram.items():
            if v == 2:
               i += 1
        
        return True if i >= 2 else False

    def is_pair(self, cards):
        symbols = [c.symbol for c in cards]
        histogram = Counter(symbols)
        for k,v in histogram.items():
            if v == 2:
                return True
        
        return False