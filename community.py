#!/usr/bin/env python3

import random
import math
from family import Family
from person import Person
from moods import MOODS
from config import *


class Community:
	'Base community class'
	__baseYear = BASE_YEAR

	def __init__(self):
		self.families = []
		self.deadFamilies = []
		self.date = 0  # SET TO 0 IF NOT
		self.harshWinter = False
		self.eventLog = []

		# generate 3 families, each with 2 adults and randomly 0-3 children
		# Do this by generating 6 adults (aged 20-40) and matching them based on romantic interest
		# Highest mutual romantic interest = pair
		tempAdults = []
		for i in range(6):
			gender = "female"
			if i % 2 == 0:
				gender = "male"

			tempAdults.append(Person([None, None], gender=gender, age=random.randint(18 * 4, 25 * 4), married=True))

		# keep track of already paired adults
		pairedInd = []
		pairs = []
		for i in range(len(tempAdults)):
			if i in pairedInd:
				continue

			highest = [0, 0]
			for j in range(i + 1, len(tempAdults)):
				if j in pairedInd or tempAdults[i].gender == tempAdults[j].gender:
					continue

				# calculate mutual romantic interest
				# This is done by dividing the sum of the interests by the difference,
				# so that values that are closer are higher-valued
				rom = tempAdults[i].calculateRomanticInterest(tempAdults[j])
				recipRom = tempAdults[j].calculateRomanticInterest(tempAdults[i])
				mutualRom = (rom+recipRom)/max(0.00001, abs(rom-recipRom))
				if mutualRom > highest[1]:
					highest = [j, mutualRom]

			pairedInd = pairedInd + [i, highest[0]]
			pairs.append([i, highest[0]])

		# now we have pairs, but as indices of tempAdults
		for pair in pairs:
			a1 = tempAdults[pair[0]]
			a2 = tempAdults[pair[1]]

			a1.partner = a2
			a2.partner = a1

			a1.updateRapport(a2, 0.7)
			a2.updateRapport(a1, 0.7)

			# Create a family for these adults
			tempFamily = Family(self)
			self.families.append(tempFamily)
			tempFamily.addPerson(a1)
			tempFamily.addPerson(a2)

			# Now generate children
			childrenCount = random.randint(2, 4)
			for i in range(childrenCount):
				child = tempFamily.generatePerson([a1, a2], age=random.randint(0, 12*4))
				a1.addChild(child)
				a2.addChild(child)
				# Make sure to set a base rapport
				a1.updateRapport(child, 0.7)
				a2.updateRapport(child, 0.7)
				child.updateRapport(a1, 0.7)
				child.updateRapport(a2, 0.7)

			# Give enough food for the year
			tempFamily.food = (10*2 + 6*childrenCount)*4

		# Pass time once without increasing the date
		self.passTime(False)

	def addFamily(self, f):
		self.families.append(f)

	def removeFamily(self, f):
		if f in self.families:
			self.families.remove(f)

	def newFamily(self, familyName=None):
		f = Family(self, familyName=familyName)
		self.addFamily(f)
		return f

	def getFamilyByIndex(self, i):
		if i < len(self.families):
			return self.families[i]
		return False

	def allPeople(self, minAge=0, maxAge=1000*4):
		tempP = []
		for f in self.families:
			for p in f.people:
				if p.age >= minAge and p.age <= maxAge:
					tempP.append(p)

		return tempP

	def graveyard(self):
		tempP = []
		for f in self.families:
			for p in f.deadPeople:
				tempP.append(p)

		return tempP

	def passTime(self, autoDateIncrease=True):
		'''
		Passes time, updating things in this order:
			1. Increase date
			2. Update moods (remove expired modifiers)
			3. Decide season events
			4. Pass time in families (subroutine)
			5. Social interactions including on-the-fly mood changes
		'''

		if autoDateIncrease:
			self.date += 1

		# update modifiers before everything else, to prevent added modifiers from being
		# immediately decreased in duration
		for p in self.allPeople():
			p.updateModifiers()

		self.log("==== {} ====".format(self.dateToString().upper()))
		if self.season() == 3:
			# harsh winter
			if random.randint(1, HARSH_WINTER_CHANCE) == 1:
				self.log("The winter is a harsh one")
				self.harshWinter = True
				for p in self.allPeople():
					p.addModifier(12)  # add 'cold' modifier
			else:
				self.harshWinter = False

		for f in self.families:
			if len(f.people) == 0:
				# everyone's died
				self.log("The old house of the {} family is left deserted".format(f.familyName))
				self.removeFamily(f)
				self.deadFamilies.append(f)

			f.passTime(self.date%4, self.harshWinter)

		for p in self.allPeople(minAge=START_INTERACTION_MIN_AGE):
			# A person interacts with 0-10 people per day, based on extroversion
			for i in range(math.ceil(p.getAttr("e")*10)):
				# This next bit works by mapping by rapport. Basically,
				# a person will be more likely to initiate social interactions
				# with someone who they have more rapport with.
				mappedByRapport = {}
				totalRapport = 0
				for i in self.allPeople():
					if i == p:
						continue

					if i in p.rapport.keys():
						mappedByRapport[i] = p.rapport[i]+1  # +1 to make positive
					else:
						mappedByRapport[i] = 1  # neutral

					# Younger people will want to talk to people of their own age.
					# So, decrease the mapping by a number based on age.
					# How doesn the formula work? Black magic and duct tape.
					# Of course, this doesn't apply to family.
					# This assumes that there is no age prejudice above 16 - TODO?
					if i not in p.family.people:
						addition = max(0,
							(8 - abs(i.age//4-p.age//4)) * max(0, ((16*4-p.age)/16*4)))
						mappedByRapport[i] = max(0, mappedByRapport[i] + addition)

					totalRapport += mappedByRapport[i]

				# Choose a person to interact with randomly, but weighted by rapport
				chosenNum = random.uniform(0, totalRapport)
				currentNum = 0
				for b in mappedByRapport.keys():
					if currentNum + mappedByRapport[b] >= chosenNum:
						# we have our person!
						# Interactions produce rapport. The person initating the
						# conversation gains more rapport for that person than the
						# person does for the initiator.
						if p.likes(b) and b.likes(p):
							if random.randint(1, DT_CHANCE) == 1 and p.age > DT_MIN_AGE and b.age > DT_MIN_AGE:
								# deep talk
								p.updateRapport(b,
									DT_RAPPORT_GAIN*(p.calculateCap(b)/CAP_MODIFIER))
								b.updateRapport(p,
									DT_RAPPORT_GAIN*(b.calculateCap(p)/CAP_MODIFIER)*INTERACTED_WITH_MOD)
								p.log("I had a deep talk with {}".format(b.printableFullName()))
								b.log("{} had a deep talk with me".format(p.printableFullName()))

								# For now, this can lead to a partnership
								# TODO change wording and other stuff for existing partner
								if p.romanticallyLikes(b) and p.age >= MIN_ASKOUT_AGE\
									and b.age >= MIN_ASKOUT_AGE and not p.married and not b.married\
									and not p.isRelative(b) and p.gender != b.gender\
									and ((p.timeWithPartner >= 2 and b.timeWithPartner >= 2) or
										(p.partner is None and b.partner is None)):
									cont = True
									# A person will only abandon a partner if the romantic interest
									# to a new person is higher
									if p.partner is not None:
										if p.calculateRomanticInterest(p.partner) >= p.calculateRomanticInterest(b):
											cont = False
									if b.partner is not None:
										if b.calculateRomanticInterest(b.partner) >= b.calculateRomanticInterest(p):
											cont = False

									if cont:
										p.log("I asked out {}".format(b.printableFullName()))
										b.log("{} asked me out".format(p.printableFullName()))
										if b.romanticallyLikes(p):
											b.log("I accepted {}'s proposal".format(p.firstName()))
											p.log("{} accepted my proposal".format(b.firstName()))
											self.log("{} and {} are now going out".format(p.printableFullName(),
												b.printableFullName()))

											if b.partner is not None:
												b.breakUp()
											if p.partner is not None:
												p.breakUp()

											b.partner = p
											p.partner = b
											b.addModifier(4)
											p.addModifier(4)
										else:
											b.log("I declined {}'s proposal".format(p.firstName()))
											p.log("{} rebuffed me".format(b.firstName()))
											p.addModifier(16)  # add rebuffed modifier
							else:
								# quick chat
								p.updateRapport(b,
									CHAT_RAPPORT_GAIN*(p.calculateCap(b)/CAP_MODIFIER))
								b.updateRapport(p,
									CHAT_RAPPORT_GAIN*(b.calculateCap(p)/CAP_MODIFIER)*INTERACTED_WITH_MOD)
								p.log("I had a quick chat with {}".format(b.printableFullName()))
								b.log("{} had a quick chat with me".format(p.printableFullName()))
						else:
							if b.age > MIN_ARGUMENT_AGE and p.age > MIN_ARGUMENT_AGE:
								p.updateRapport(b, ARGUMENT_RAPPORT_GAIN*INTERACTED_WITH_MOD)
								b.updateRapport(p, ARGUMENT_RAPPORT_GAIN)
								p.log("I had an argument with {}".format(b.printableFullName()))
								b.log("{} had an argument with me".format(p.printableFullName()))
							else:
								p.updateRapport(b, ANGRY_LOOK_RAPPORT_GAIN*INTERACTED_WITH_MOD)
								b.updateRapport(p, ANGRY_LOOK_RAPPORT_GAIN)
								p.log("I gave {} an angry look".format(b.printableFullName()))
								b.log("{} gave me an angry look".format(p.printableFullName()))
						break
					else:
						currentNum += mappedByRapport[b]

	def log(self, s):
		self.eventLog.append(s)

	def season(self):
		return self.date%4

	def seasonToString(self, n):
		n = n%4
		if n == 0:
			return "Spring"
		elif n == 1:
			return "Summer"
		elif n == 2:
			return "Autumn"
		elif n == 3:
			return "Winter"

	def dateToString(self):
		return "{} of the year {}".format(self.seasonToString(self.date), self.__baseYear+(self.date//4))

	def __str__(self):
		toReturn = []
		for f in self.families:
			toReturn.append("\n{}".format(str(f)))

		return "\n".join(toReturn)
