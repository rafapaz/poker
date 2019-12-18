from player import Player
from poker import Poker

if __name__ == "__main__":
    p1 = Player('P1', 1000)
    p2 = Player('P2', 1000)
      
    poker = Poker()
    poker.register_player(p1)
    poker.register_player(p2)

    poker.start_game()    
    poker.deliver()

    poker.reveal_card()
    poker.reveal_card()
    poker.reveal_card()
    poker.reveal_card()
    poker.reveal_card()

    win, score = poker.winner()
    if win.name == 'P1':
        print('{} -> {}'.format([str(c) for c in (win.cards + poker.table_cards)], score))
    