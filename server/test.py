import unittest
from player import Player
from poker import Poker
from card import Card

class TestPoker(unittest.TestCase):
    
    def setUp(self):
        p1 = Player('P1', 1000)
        p2 = Player('P2', 1000)
        self.poker = Poker([p1, p2])

    def test_royalflush(self):        
        cards1 = [Card('spade','10', 0), Card('spade','J', 0), Card('spade','Q', 0), Card('club','5', 0), Card('club','8', 0), Card('spade','A', 0), Card('spade','K', 0)]        
        self.assertEqual(self.poker.is_royalflush(cards1), True)

        cards2 = [Card('spade','10', 0), Card('spade','4', 0), Card('spade','Q', 0), Card('club','5', 0), Card('club','8', 0), Card('spade','A', 0), Card('spade','K', 0)]
        self.assertEqual(self.poker.is_royalflush(cards2), False)

    def test_straightflush(self):
        cards1 = [Card('spade','4', 4), Card('spade','5', 5), Card('spade','6', 6), Card('club','5', 5), Card('club','8', 8), Card('spade','8', 8), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_straightflush(cards1), True)

        cards2 = [Card('heart','9', 9), Card('spade','5', 5), Card('spade','6', 6), Card('club','5', 5), Card('club','8', 8), Card('spade','8', 8), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_straightflush(cards2), False)

    def test_fourofakind(self):
        cards1 = [Card('spade','4', 4), Card('heart','4', 4), Card('spade','6', 6), Card('club','5', 5), Card('club','4', 4), Card('diamond','4', 8), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_fourofakind(cards1), True)

        cards2 = [Card('spade','4', 4), Card('heart','9', 4), Card('spade','6', 6), Card('club','5', 5), Card('club','4', 4), Card('diamond','4', 8), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_fourofakind(cards2), False)

    def test_fullhouse(self):
        cards1 = [Card('spade','4', 4), Card('heart','2', 2), Card('spade','10', 10), Card('club','7', 7), Card('club','4', 4), Card('diamond','4', 4), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_fullhouse(cards1), True)

        cards2 = [Card('spade','4', 4), Card('heart','9', 9), Card('spade','6', 6), Card('club','5', 5), Card('club','4', 4), Card('diamond','4', 4), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_fullhouse(cards2), False)

    def test_flush(self):
        cards1 = [Card('spade','4', 4), Card('heart','2', 2), Card('spade','10', 10), Card('club','7', 7), Card('spade','J', 11), Card('spade','8', 8), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_flush(cards1), True)

        cards2 = [Card('spade','4', 4), Card('heart','9', 9), Card('spade','6', 6), Card('club','5', 5), Card('club','4', 4), Card('diamond','4', 8), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_flush(cards2), False)

    def test_straight(self):
        cards1 = [Card('spade','4', 4), Card('heart','2', 2), Card('diamond','5', 5), Card('club','8', 8), Card('heart','J', 11), Card('spade','6', 6), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_straight(cards1), True)

        cards2 = [Card('club','8', 8), Card('spade','K', 13), Card('spade','7', 7), Card('spade','9', 9), Card('diamond','J', 11), Card('heart','6', 6), Card('club','A', 14)]        
        self.assertEqual(self.poker.is_straight(cards2), False)

    def test_threeofakind(self):
        cards1 = [Card('spade','4', 4), Card('heart','7', 7), Card('diamond','5', 5), Card('club','7', 7), Card('heart','J', 11), Card('spade','K', 13), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_threeofakind(cards1), True)

        cards2 = [Card('spade','2', 2), Card('heart','9', 9), Card('spade','6', 6), Card('club','5', 5), Card('club','4', 4), Card('diamond','4', 4), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_threeofakind(cards2), False)

    def test_twopair(self):
        cards1 = [Card('spade','4', 4), Card('heart','7', 7), Card('diamond','5', 5), Card('club','2', 2), Card('heart','J', 11), Card('spade','5', 5), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_twopair(cards1), True)

        cards2 = [Card('spade','2', 2), Card('heart','9', 9), Card('spade','6', 6), Card('club','5', 5), Card('club','4', 4), Card('diamond','4', 4), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_twopair(cards2), False)

    def test_pair(self):
        cards1 = [Card('spade','4', 4), Card('heart','7', 7), Card('diamond','5', 5), Card('club','2', 2), Card('heart','J', 11), Card('spade','K', 13), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_pair(cards1), True)

        cards2 = [Card('spade','2', 2), Card('heart','9', 9), Card('spade','6', 6), Card('club','5', 5), Card('club','4', 4), Card('diamond','K', 13), Card('spade','7', 7)]        
        self.assertEqual(self.poker.is_pair(cards2), False)

if __name__ == '__main__':
    unittest.main()