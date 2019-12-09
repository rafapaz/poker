
from player import Player
from poker import Poker

if __name__ == "__main__":
    p1 = Player('P1', 1000)
    p2 = Player('P2', 1000)
    p3 = Player('P3', 1000)

    
    poker = Poker()
    poker.register_player(p1)
    poker.register_player(p2)
    poker.register_player(p3)
    poker.deliver()
    print(p1)
    print(p2)
    print(p3)
    for i, p in enumerate(poker.players):
        if i == 0:
            poker.get_money(p.give_money(50))
        elif i == 1:
            poker.get_money(p.give_money(100))

    
    print([str(p) for p in poker.players])   
        
    poker.reveal_card()
    poker.reveal_card()
    poker.reveal_card()
    poker.reveal_card()
    poker.reveal_card()
    
    print('Table: {} / {}'.format([str(c) for c in poker.table_cards], poker.table_money))

    win, score = poker.winner()

    print('Winner: ' + win.name + ' with ' + score)
    print([str(p) for p in poker.players]) 
    #poker.unregister_player(p1)
    #poker.unregister_player(p2)
    #poker.unregister_player(p3)

    #print(poker.players)