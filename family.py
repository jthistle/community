#!/usr/bin/env python3

import random
import math
from namegen import NameGen
from person import Person
from config import *

nameGen = NameGen()


class Family:
	'Base family class'
	__professions = PROFESSIONS

	def __init__(self, community, familyName=None):
		self.people = []
		self.deadPeople = []
		self.food = 0
		self.profession = random.choice(self.__professions)
		self.eventLog = []
		self.community = community

		if familyName is not None:
			self.familyName = familyName
		else:
			self.familyName = nameGen.last()

	def addPerson(self, p, preserveSurname=False):
		if not preserveSurname:
			p.setSurname(self.familyName)
		p.family = self
		self.people.append(p)

	def generatePerson(self, parents, gender="", age=0):
		newP = Person(parents, gender=gender, surname=self.familyName, age=age)

		numerals = ["II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV",
			"XV", "XVI", "XVII", "XVIII", "XIX", "XX"]
		highest = -2
		for p in self.people:
			if len(p.firstName().split(" ")) == 1:
				firstbit = p.firstName()
			else:
				firstbit = " ".join(p.firstName().split(" ")[:-1])

			lastbit = p.firstName().split(" ")[-1]
			if firstbit == newP.firstName():
				if lastbit in numerals:
					if numerals.index(lastbit) > highest:
						highest = numerals.index(lastbit)
				elif highest == -2:
					highest = -1

		if highest >= -1 and highest+1 < len(numerals):
			newP.setFirstName(newP.firstName()+" "+numerals[highest+1])

		self.addPerson(newP)
		return newP

	def getPerson(self, i):
		try:
			return self.people[i]
		except Exception as e:
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
			toLog = "{} died at the age of {}".format(p.printableFullName(), p.ageToString())
			self.log(toLog)
			self.community.log(toLog)

			# apply mood modifiers to:
			# parents, siblings, children
			if p.parents[0] is not None:
				for i in p.parents:
					i.addModifier(8)
				for i in p.parents[0].children:
					if i != p:
						i.addModifier(9)

			for i in p.children:
				i.addModifier(7)
			if p.partner is not None:
				if p.married:
					p.partner.addModifier(11)
				else:
					p.partner.addModifier(10)
					p.partner.partner = None
					p.partner = None

	def seasonToString(self, n):
		# Duplicate code, TODO move?
		n = n%4
		if n == 0:
			return "Spring"
		elif n == 1:
			return "Summer"
		elif n == 2:
			return "Autumn"
		elif n == 3:
			return "Winter"

	def log(self, s):
		self.eventLog.append(s)

	def passTime(self, season, harshWinter):
		self.log("== {} ==".format(self.seasonToString(season)))

		adults = 0
		children = 0
		workingChildren = 0

		for p in self.people:
			if p.isChild():
				children += 1
				if p.age > WORKING_CHILD_MIN_AGE:
					workingChildren += 1
			else:
				adults += 1
			p.passTime()

		# This flag decides if the good harvest modifier is set or not
		goodHarvest = False
		# This flag decides if the made a profit modifier is set or not
		madeProfit = False

		if self.profession == "farmer":
			# Is it time to harvest?
			if season == 2:
				yieldModifier = min(1.2, max(0.8, random.gauss(1, 0.1)))
				if harshWinter:
					yieldModifier *= HARSH_WINTER_MOD
					self.log("The harsh winter has reduced yields")

				if yieldModifier >= 1:
					goodHarvest = True
					self.log("It has been a good harvest for the {} family".format(self.familyName))

				startFood = self.food
				self.food += ADULT_BASE_HARVEST*yieldModifier*adults
				self.food += CHILD_BASE_HARVEST*yieldModifier*workingChildren
				self.food = round(self.food)
				self.log("The family harvested {} units of food".format(self.food-startFood))
		elif self.profession == "merchant":
			# A merchant's income is a function of their intelligence,
			# and is slightly random.
			# Only adults can work as a merchant.

			startFood = self.food  # used to calculate profit

			baseIncome = MERCHANT_BASE_INCOME
			incomeModifier = min(1.5, max(0.5, random.gauss(1, 0.2)))
			for p in self.people:
				if p.isChild():
					continue
				intelligenceModifier = p.getAttr("i")-0.5
				self.food += (baseIncome*incomeModifier) + (baseIncome*intelligenceModifier)
			self.food = round(self.food)

		# Calculate food shares
		# Prioritise child food
		childFood = 0
		adultFood = 0

		if children > 0:
			childFood = min(CHILD_FOOD_NOURISHED, self.food // children)
			self.food -= childFood * children
		if adults > 0:  # should always be true
			adultFood = min(ADULT_FOOD_NOURISHED, self.food // adults)
			self.food -= adultFood * adults

		for p in self.people:
			if p.isChild():
				if childFood == CHILD_FOOD_NOURISHED:
					p.addModifier(0)
				elif childFood > CHILD_FOOD_HUNGRY:
					p.addModifier(1)
				elif childFood > CHILD_FOOD_MALNOURISHED:
					p.addModifier(2)
					self.log("{} is malnourised".format(p.firstName()))
				else:
					p.addModifier(3)
					self.log("{} is starving".format(p.firstName()))
			else:
				if adultFood == ADULT_FOOD_NOURISHED:
					p.addModifier(0)
				elif childFood > ADULT_FOOD_HUNGRY:
					p.addModifier(1)
				elif childFood > ADULT_FOOD_MALNOURISHED:
					p.addModifier(2)
					self.log("{} is malnourished".format(p.firstName()))
				else:
					p.addModifier(3)
					self.log("{} is starving".format(p.firstName()))

		if self.profession == "merchant":
			if self.food > startFood:
				madeProfit = True
				self.log("The family made a profit of {} units of food".format(self.food-startFood))
			else:
				self.log("The family made a loss of {} units of food".format(self.food-startFood))
		elif self.profession == "farmer":
			# just some flavour text
			if season == 0:
				self.log("The family is sowing the fields")
			elif season == 3:
				self.log("The remains of the harvest wither and die in the cold")

		for p in self.people:
			if goodHarvest:
				p.addModifier(13)
			if madeProfit:
				p.addModifier(14)

		if self.food > len(self.people)*MAX_FOOD_STORAGE_PER_PERSON:
			self.food = len(self.people)*MAX_FOOD_STORAGE_PER_PERSON
			self.log("The family struggles to store so much food, and some of it perishes")

		self.log("The family ends the season with {} units of food".format(self.food))

	def inspect(self):
		'''
		Returns some text for the GUI inspector
		'''
		toReturn = []
		toReturn.append("== The {} family ==".format(self.familyName.upper()))
		toReturn.append("A family of {}s".format(self.profession))
		toReturn.append("The family posesses {} units of food".format(self.food))
		return "\n".join(toReturn)

	def __str__(self):
		toReturn = []
		toReturn.append("==== The {} family, a family of {}s ====".format(self.familyName.upper(), self.profession))
		for p in self.people:
			toReturn.append("{}, age {}, feeling {}".format(p.printableFullName(), p.ageToString(), p.oneWordMood()))

		toReturn.append("The family posesses {} units of food".format(self.food))

		return "\n".join(toReturn)
