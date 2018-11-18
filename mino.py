#! /usr/bin/env python2.7
"""
Author: Josh Miller
"""
from __future__ import division
import random

CARDS_IN_HAND = 3
NUM_PLAYERS = 3
DEBUG = True

class Card:

	def __init__(self, n, q, a):
		self.name = n
		self.quirks = q
		self.ability = a
		
	def has_quirk(self, q):
		if q in self.quirks:
			return True
		return False
		
	def __repr__(self):
		return "<Card " + str(id(self)) + ": " + self.name + " " + str(self.quirks) + " " + str(self.ability) + ">"
	
	def __str__(self):
		return self.name
	

class Pile:
	
	def __init__(self, c, q):
		self.card = c
		self.quantity = q
		
	def draw(self):
		self.quantity -= 1
		return self.card
		
	def __repr__(self):
		return "<Pile " + str(id(self)) + ": " + str(self.card) + " " + str(self.quantity) + ">"
	
	def __str__(self):
		return str(self.card) + "(" + str(self.quantity) + ")"
	
	
class Table:
	
	def __init__(self, cards, num_players):
		self.piles = []
		self.quantity = 0
		for card in cards:
			self.piles.append(Pile(card, num_players))
			self.quantity += num_players
			
	def draw(self):
		self.quantity -= 1
		return self.piles
		
	def __repr__(self):
		return "<Table " + str(id(self)) + ": " + str(self.piles) + " " + str(self.quantity) + ">"
	
	def __str__(self):
		return "Table" + "(" + str(self.quantity) + ")" + str(self.piles) 
		
class Player:
	
	# randomly draw a card
	def default_draw_behavior(self):
		piles = self.table.draw()
		while(True):
			for pile in piles:
				if pile.quantity > 0:
					if random.random() < (1.0 / len(piles)):
						card = pile.draw()
						if DEBUG:
							print(self.name + " drew " + str(card))
						return card
	
	def __init__(self, n, t, d=default_draw_behavior):
		self.name = n
		self.hand = []
		self.table = t
		self.draw_behavior = d
		self.sets = []
						
						
	def draw(self):
		return self.draw_behavior(self)
	
	def print_hand(self):
		ret = "("
		i = 0
		while i < len(self.hand):
			ret += str(self.hand[i])
			if i != len(self.hand) - 1:
				ret += ", "
			i += 1
		ret += ")"
		return ret
	
	def __repr__(self):
		return "<Player " + str(id(self)) + ": " + self.print_hand() + " " + str(self.quantity) + " " + str(draw_behavior) + ">"
	
	def __str__(self):
		return self.name + "(" + str(len(self.hand)) + "): " + self.print_hand()

	

def play_game(players, table):
	
	# OPENING PHASE
	round = 0
	while (round < CARDS_IN_HAND):
		for player in players:
			player.hand.append(player.draw())
		round +=1
		
	if DEBUG:
		print("At the end of the opening phase, hands are: ")
		for player in players:
			print(player)
	
	
	# TRADING PHASE
	
	# SCORING PHASE


def setup(args):

	cards = []
	cards.append(Card("Card A", ["Quirk 1", "Quirk 2", "Quirk 3"], "ability 1"))
	cards.append(Card("Card B", ["Quirk 1", "Quirk 3", "Quirk 4"], "ability 2"))
	cards.append(Card("Card C", ["Quirk 2", "Quirk 4", "Quirk 3"], "ability 3"))
	cards.append(Card("Card D", ["Quirk 1", "Quirk 2", "Quirk 4"], "ability 4"))
	
	table = Table(cards, 3)
	
	players = []
	players.append(Player("Alice", table))
	players.append(Player("Bob", table))
	players.append(Player("Charlie", table))
	
	play_game(players, table)



def main():
	import argparse
	prog_desc = "Automated playtesting of Mino, a strategic set building game about amino acids."
	parser = argparse.ArgumentParser(description=prog_desc)
	#parser.add_argument('input', help="Input file name")
	#parser.add_argument('output', help="Output file name")
	args = parser.parse_args()
	setup(args)
	

if '__main__' == __name__:
	main()