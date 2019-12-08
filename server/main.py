
from player import Player
from poker import Poker

if __name__ == "__main__":
    p1 = Player('P1', 1000)
    p2 = Player('P2', 1000)
    p3 = Player('P3', 1000)

    poker = Poker([p1, p2, p3])
    poker.deliver()
    print(p1)
    print(p2)
    print(p3)
    poker.reveal_card()
    poker.reveal_card()
    poker.reveal_card()
    poker.reveal_card()
    poker.reveal_card()
    print('Table: {}'.format([str(c) for c in poker.table_cards]))

    win, score = poker.winner()

    print('Winner: ' + win.name + ' with ' + score)