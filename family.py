#!/usr/bin/env python3

import random, math
from namegen import NameGen
from person import Person
from moods import MOODS

nameGen = NameGen()

class Family:
	'Base family class'
	 # change according to probability
	__professions = ["farmer"]*2 + ["merchant"]

	def __init__(self):
		self.people = []
		self.deadPeople = []
		self.familyName = nameGen.last()
		self.food = 0
		self.profession = random.choice(self.__professions)

	def addPerson(self, p, preserveSurname=False):
		if not preserveSurname:
			p.setSurname(self.familyName)
		p.family = self
		self.people.append(p)

	def generatePerson(self, parents, gender="", age=0):
		newP = Person(parents, gender=gender, surname=self.familyName, age=age)
		## TODO: if name is the same, add a II, if that's taken, then a III etc.

		self.addPerson(newP)
		return newP

	def getPerson(self, i):
		try:
			return self.people[i]
		except:
			return False

	def removePerson(self, p):
		'''
		Removes first (and probably only) occurence of person from family.
		'''
		if self.people.count(p) != 0:
			self.people.remove(p)

	def removePersonByIndex(self, i):
		if len(self.people) > i:
			del self.people[i]

	def memberDied(self, p):
		if p in self.people:
			self.removePerson(p)
			self.deadPeople.append(p)
			# apply mood modifiers to:
			# parents, siblings, children
			for i in p.parents:
				i.addModifier(8)
			for i in p.children:
				i.addModifier(7)
			for i in p.parents[0].children:
				if i != p:
					i.addModifier(9)
			if p.partner != None:
				if p.married:
					p.partner.addModifier(11)
				else:
					p.partner.addModifier(10)

	def passTime(self, season, harshWinter):
		# Family actions TODO
		# - Calculate income of food (DONE)
		# - Share out food (DONE)
		# - Individual pass time (WIP)
		# - Adjust merchant and farmer incomes (either too high or low)
		print("\nEvents for the {} family".format(self.familyName.upper()))

		adults = 0
		children = 0
		workingChildren = 0

		for p in self.people:
			if p.isChild():
				children += 1
				if p.age > 8*4: # TODO hardcoded
					workingChildren += 1
			else:
				adults += 1
			p.passTime()
			if not p.alive:
				self.removePerson(p)
				self.deadPeople.append(p)

		if len(self.people) == 0:
			print("The house of the {} family is deserted.".format(self.familyName))
			return

		# This flag decides if the good harvest modifier is set or not
		goodHarvest = False
		# This flag decides if the made a profit modifier is set or not
		madeProfit = False

		if self.profession == "farmer":
			# Is it time to harvest?
			if season == 2:
				yieldModifier = min(1.2, max(0.8, random.gauss(1, 0.1)))
				if harshWinter:
					yieldModifier *= 0.5 # TODO hardcoded
					print("The harsh winter has reduced yields")

				if yieldModifier >= 1:
					goodHarvest = True
					print("It has been a good harvest for the {} family".format(self.familyName))

				startFood = self.food
				self.food += 50*yieldModifier*adults # TODO hardcoded
				self.food += 25*yieldModifier*workingChildren # and here
				self.food = round(self.food)
				print("The family harvested {} units of food".format(self.food-startFood))
		elif self.profession == "merchant":
			# A merchant's income is a function of their intelligence,
			# and is slightly random.
			# Only adults can work as a merchant.

			startFood = self.food # used to calculate profit

			baseIncome = 15 # TODO hardcoded
			incomeModifier = min(1.5, max(0.5, random.gauss(1, 0.2)))
			for p in self.people:
				if p.isChild():
					continue
				intelligenceModifier = p.getAttr("i")-0.5
				self.food += (baseIncome*incomeModifier) + (baseIncome*intelligenceModifier)
			self.food = round(self.food)

		# Calculate food shares
		# Prioritise child food
		# TODO hardcoded - A lot of these values are hardcoded
		# and should really be stored in a config file somewhere.
		childFood = 0
		adultFood = 0 

		if children > 0:
			childFood = min(6, self.food // children)
			self.food -= childFood * children
		if adults > 0: # should always be true
			adultFood = min(10, self.food // adults)
			self.food -= adultFood * adults

		# print("Debug: childFood = {}   adultFood = {}".format(childFood, adultFood))

		# TODO hardcoded - loads of values here
		for p in self.people:
			if p.isChild():
				if childFood == 6:
					p.addModifier(0)
				elif childFood > 4:
					p.addModifier(1)
				elif childFood > 2:
					p.addModifier(2)
					print("{} is malnourised".format(p.firstName()))
				else:
					p.addModifier(3)
					print("{} is starving".format(p.firstName()))
			else:
				if adultFood == 10:
					p.addModifier(0)
				elif childFood > 7:
					p.addModifier(1)
				elif childFood > 4:
					p.addModifier(2)
					print("{} is malnourished".format(p.firstName()))
				else:
					p.addModifier(3)
					print("{} is starving".format(p.firstName()))

		if self.profession == "merchant":
			if self.food > startFood:
				madeProfit = True
				print("The family made a profit of {} units of food".format(self.food-startFood))
			else:
				print("The family made a loss of {} units of food".format(self.food-startFood))
		elif self.profession == "farmer":
			# just some flavour text
			if season == 0:
				print("The family is sowing the fields")
			elif season == 3:
				print("The remains of the harvest wither and die in the cold")


		for p in self.people:
			if goodHarvest:
				p.addModifier(13)
			if madeProfit:
				p.addModifier(14)

		if self.food > len(self.people)*100:
			self.food = len(self.people)*100
			print("The family struggles to store so much food, and some of it perishes")
		print("The family ends the season with {} units of food".format(self.food))

	def __str__(self):
		toReturn = []
		toReturn.append("==== The {} family, a family of {}s ====".format(self.familyName.upper(), self.profession))
		for p in self.people:
			toReturn.append("{}, age {}, feeling {}".format(p.printableFullName(), p.ageToString(), p.oneWordMood()))

		toReturn.append("The family posesses {} units of food".format(self.food))

		return "\n".join(toReturn)