#! /usr/bin/env python2.7
"""
Author: Josh Miller
"""
from __future__ import division
from sets import Set
from collections import defaultdict
import random
import copy
#import threading


DEBUG_LEVEL = 1

# TODO
# - Add Abilities
# - Add Information Modeling
# - Add non-default behaviors
# - Allow for human input

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
		piles = self.game.table.draw()
		while(True):
			pile = random.choice(piles)
			if pile.quantity > 0:
				card = pile.draw()
				return card
						
	# randomly choose a player, ask for random card
	def default_trade_behavior(self):
		donor = None
		while donor is None or donor is self:
			donor = random.choice(self.game.players)
		card = random.choice(self.game.table.piles).card
		return card, donor
		
	# pick a random card to return
	def default_give_back_behavior(self):
		return self.give(random.choice(self.hand))
		
	# pick a random card to play
	def default_play_from_hand_behavior(self):
		return self.give(random.choice(self.hand))
		
	# if have card, give; else give nothing
	def default_respond_to_trade_behavior(self, card):
		if card in self.hand:
			return self.give(card)
		else:
			return None
		
		
	# greedily maximize highest scoring set
	def default_play_behavior(self, card):
		if [] not in self.sets:
			self.sets.append([]) # we can always start a new set
		best_set = None
		best_score = -1
		for set in self.sets:
			potential_set = copy.copy(set)
			potential_set.append(card)
			score = self.calculate_score(potential_set)
			if score > best_score:
				best_score = score
				best_set = set
		return card, best_set
	
	def __init__(self, n, g, draw_behavior=default_draw_behavior,
				trade_behavior=default_trade_behavior, 
				play_from_hand_behavior=default_play_from_hand_behavior,
				respond_to_trade_behavior=default_respond_to_trade_behavior,
				give_back_behavior=default_give_back_behavior,
				play_behavior=default_play_behavior):
		self.sets = []
		self.name = n
		self.hand = []
		self.game = g
		self.draw_behavior = draw_behavior
		self.trade_behavior = trade_behavior
		self.play_from_hand_behavior = play_from_hand_behavior
		self.respond_to_trade_behavior = respond_to_trade_behavior
		self.give_back_behavior = give_back_behavior
		self.play_behavior = play_behavior
		
	
	# TODO hard code in special abilities
	def calculate_score(self, set):
		size = len(set)
		if size < 1:
			return 0
		else:
			shared_quirks = Set(set[0].quirks)
			for card in set:
				shared_quirks = shared_quirks & Set(card.quirks)
		if DEBUG_LEVEL > 1:
			print("Considering the set " + print_cards(set) + ", it has a size of " + str(size) \
				+ " and shares " + str(len(shared_quirks)) + " quirks: " + str(shared_quirks))
		return len(shared_quirks) * size
		


	# remove the card from our hand and return it
	def give(self, card):
		assert card in self.hand
		self.hand.remove(card)
		if DEBUG_LEVEL > 0:
			print(self.name + " removes " + str(card) + " from their hand.")
		return card

	# using draw behavior, add a card from a pile to our hand
	def draw(self):
		card = self.draw_behavior(self)
		if DEBUG_LEVEL > 0:
			print(self.name + " drew " + str(card) + " into their hand: " + print_cards(self.hand + [card]))
		return card
		
	# using trade behavior, choose someone to ask for a card, swap cards if needed, play trades
	def trade(self):
		card, donor = self.trade_behavior(self)
		assert donor != self
		if DEBUG_LEVEL > 0:
			print(self.name + " asked " + str(donor.name) + " for " + str(card))
			print(str(donor.name) + "\'s hand is " + print_cards(donor.hand))
		received = donor.respond_to_trade(card)
		if received is None:
			# Play from hand
			if len(self.hand) > 0:
				received = self.play_from_hand()
				self.play(received)
		else:
			self.play(received)
			donor.play(self.give_back()) # donor plays what we give them in return
		return card, donor
		
		
	def play(self, card):
		card, set = self.play_behavior(self, card)
		for s in self.sets:
			if s is set:
				s.append(card)
		if DEBUG_LEVEL > 0:
			print(self.name + " played " + str(card) + " into " + print_cards(set))
		
	def play_from_hand(self):
		card = self.play_from_hand_behavior(self)
		if DEBUG_LEVEL > 0:
			print(self.name + " played " + str(card) + " from their hand")
		return card
		
	def respond_to_trade(self, card):
		ret = self.respond_to_trade_behavior(self, card)
		if DEBUG_LEVEL > 0: 
			print(self.name + " gave " + str(ret))
		return ret
		
	def give_back(self):
		ret = self.give_back_behavior(self)
		if DEBUG_LEVEL > 0:
			print(self.name + " gave " + str(ret) + " in return")
		return ret
		
	def play_all_in_hand(self):
		while len(self.hand) > 0:
			self.play(self.play_from_hand())
	
	def __repr__(self):
		return "<Player " + str(id(self)) + ": " + print_cards(self.hand) + " " + str(self.quantity) + " " + str(draw_behavior) + ">"
	
	def __str__(self):
		return self.name + "(" + str(len(self.hand)) + "): " + print_cards(self.hand)

	
class Game:

	def __init__(self, table):
		self.table = table
		self.players = []
		
	def add_player(self, player):
		self.players.append(player)
		


def assert_card_accountability(game):
	global args
	if not DEBUG_LEVEL: # when not debugging, don't check card accountability
		return
		
	card_dict = defaultdict(int)
	for pile in game.table.piles:
		card_dict[pile.card] += pile.quantity			
	for player in game.players:
		for card in player.hand:
			card_dict[card] += 1
		for set in player.sets:
			for card in set:
				card_dict[card] += 1
	
	
	issue_cards = []
	for card, quantity in card_dict.items():
		if quantity != args.players:
			issue_cards.append(card)
			print("ERROR: Cards duplicated or lost, " + str(card) + " -> " + str(quantity))
			for pile in game.table.piles:
				if pile.card == card:
					print("---Pile quantity: " + str(pile.quantity))
			for player in game.players:
				for c in player.hand:
					if card == c:
						print("---And 1 in the hand of " + player.name)
				for set in player.sets:
					for c in set:
						if card == c:
							print("---And 1 in the set of " + player.name + ", " + print_cards(set))
			
	if len(issue_cards):
		exit(1)
		
	
		
def play_game(game):
	global args

	random.seed()
	
	players = game.players
	table = game.table
	
	# OPENING PHASE
	if DEBUG_LEVEL > 0:
		print("\nOPENING PHASE")
	round = 0
	while (round < args.handsize):
		for player in players:
			if DEBUG_LEVEL > 0:
				print("\n" + str(player.name) + "\'s turn")
			player.hand.append(player.draw())
		round +=1
		
	if DEBUG_LEVEL > 0:
		print("\nAt the end of the opening phase, hands are: ")
		for player in players:
			print(player)
		print("\n")
	
	
	assert_card_accountability(game)
	
	# TRADING PHASE
	if DEBUG_LEVEL > 0:
		print("\nTRADING PHASE")
	while (table.quantity > 0):
		for player in players:
			if DEBUG_LEVEL > 0:
				print("\n" + str(player.name) + "\'s turn")
			player.hand.append(player.draw())
			player.trade()
			assert_card_accountability(game)
			
		round +=1
	
	if DEBUG_LEVEL > 0:
		print("\nAt the end of the trading phase, these are the players' hands and sets: ")
		for player in players:
			print(player)
			for set in player.sets:
				if len(set) > 0:
					print("   " + print_cards(set))
		
	
	assert_card_accountability(game)
	
	# SCORING PHASE
	# (although threads could simulate everyone doing it at once, I'm worried about concurrency issues)
	for player in players:
		if DEBUG_LEVEL > 0:
			print("\n" + str(player.name) + " is playing cards from their hand into their sets.")
		player.play_all_in_hand()
		
	if DEBUG_LEVEL > 0:
		print("\nAt the end of the scoring phase, these are the players' sets: ")
		for player in players:
			print(player.name)
			for set in player.sets:
				if len(set) > 0:
					print("   " + print_cards(set))
					
	print("")
		
	# calculate final scores
	best_score = -1
	best_player = None
	for player in players:
		players_best_score = -1
		players_best_set = None
		for set in player.sets:
			score = player.calculate_score(set)
			if score > players_best_score:
				players_best_score = score
				players_best_set = set
				if score > best_score:
					best_score = score
					best_player = player
		print(str(player.name) + " scored " + str(players_best_score) + " with this set: " + print_cards(players_best_set))
	
	assert_card_accountability(game)
	
	print("\n" + str(best_player.name) + " wins!")


def print_cards(set):
	ret = "("
	i = 0
	while i < len(set):
		ret += str(set[i])
		if i != len(set) - 1:
			ret += ", "
		i += 1
	ret += ")"
	return ret
	
def setup():
	global args

	cards = []
	cards.append(Card("Ala", ["Aliphatic", "Hydrophobic", "Tiny", "Alkyl group"], "Alanine Ambivalence"))
	cards.append(Card("Ile", ["Aliphatic", "Hydrophobic", "Essential", "Alkyl group", "Glucogenic"], "Branched-Chain Isoleucine"))
	cards.append(Card("Leu", ["Aliphatic", "Hydrophobic", "Essential", "Alkyl group", "Ketogenic"], "Branched-Chain Leucine"))
	cards.append(Card("Met", ["Hydrophobic", "Essential", "Sulfur-containing", "Nonpolar"], "Start Codon"))
	cards.append(Card("Val", ["Aliphatic", "Hydrophobic", "Essential", "Alkyl group"], "Branched-Chain Valine"))
	cards.append(Card("Phe", ["Aromatic", "Hydrophobic", "Essential", "Nonpolar", "Glucogenic"], "Tyrosine Synthesis"))
	cards.append(Card("Trp", ["Aromatic", "Hydrophobic", "Essential", "Nonpolar", "Glucogenic"], "Serotonin Synthesis"))
	cards.append(Card("Tyr", ["Aromatic", "Hydrophobic", "Conditionally Essential", "Polar", "Glucogenic"], "Dopamine Synthesis"))
	cards.append(Card("Asn", ["Polar", "Nonessential", "Amide"], "Asparagus, A Pair of Us"))
	cards.append(Card("Cys", ["Nonpolar", "Sulfur-containing"], "Disulfide Bridge"))
	cards.append(Card("Gln", ["Polar", "Conditionally Essential", "Amide"], "Abundant Regulator"))
	cards.append(Card("Ser", ["Polar", "Conditionally Essential", "Hydroxyl-containing", "Tiny"], "Tiny Bonus"))
	cards.append(Card("Thr", ["Polar", "Essential", "Hydroxyl-containing", "Glucogenic"], "Last Discovery"))
	cards.append(Card("Asp", ["Acidic", "Negative", "Charged", "Nonessential"], "Charge Bonus Aspartate"))
	cards.append(Card("Glu", ["Acidic", "Negative", "Charged", "Nonessential"], "GABA Synthesis"))
	cards.append(Card("Arg", ["Basic", "Positive", "Charged", "Conditionally Essential"], "Charge Bonus Arginine"))
	cards.append(Card("His", ["Aromatic", "Basic", "Positive", "Charged", "Essential"], "Inflammation"))
	cards.append(Card("Lys", ["Basic", "Positive", "Charged", "Essential", "Ketogenic"], "Ketone Body"))
	cards.append(Card("Gly", ["Conditionally Essential", "Alkyl group", "Tiny"], "Glycine Ambivalence"))
	cards.append(Card("Pro", ["Conditionally Essential", "Nonpolar", "Tiny"], "Double Bind"))

	card_subset = random.sample(cards, args.numpiles)
	
	table = Table(card_subset, 3)
	game = Game(table)
	
	game.add_player(Player("Alice", game))
	game.add_player(Player("Bob", game))
	game.add_player(Player("Charlie", game))
	
	print("Playing a game with these cards: " + print_cards(card_subset))
	
	play_game(game)



def main():
	import argparse
	global args
	global DEBUG_LEVEL
	prog_desc = "Automated playtesting of Mino, a strategic set building game about amino acids."
	parser = argparse.ArgumentParser(description=prog_desc)
	parser.add_argument('players', default=3, help="Number of players")
	parser.add_argument('handsize', default=5, help="Number of cards in hand")
	parser.add_argument('numpiles', default=10, help="Number of unique cards (piles) to use in the game")
	parser.add_argument('debug', default=0, help="Level of debugging detail")
	args = parser.parse_args()
	if args.debug > DEBUG_LEVEL:
		DEBUG_LEVEL = args.debug
	setup()
	

if '__main__' == __name__:
	main()