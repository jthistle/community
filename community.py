#!/usr/bin/env python3

import random, math
from family import Family
from person import Person
from moods import MOODS

class Community:
	'Base community class'
	__baseYear = 1043

	def __init__(self):
		self.families = []
		self.date = 0 # SET TO 0 IF NOT
		self.harshWinter = False

		# generate 3 families, each with 2 adults and randomly 0-3 children
		# Do this by generating 6 adults (aged 20-40) and matching them based on romantic interest
		# Highest mutual romantic interest = pair
		tempAdults = []
		for i in range(6):
			gender = "female"
			if i%2 == 0:
				gender = "male"

			tempAdults.append(Person([None, None], gender=gender, age=random.randint(18*4,25*4), married=True))

		# keep track of already paired adults
		pairedInd = []
		pairs = []
		for i in range(len(tempAdults)):
			if i in pairedInd:
				continue

			highest = [0, 0]
			for j in range(i+1, len(tempAdults)):
				if j in pairedInd or tempAdults[i].gender == tempAdults[j].gender:
					continue 

				# calculate mutual romantic interest
				# This is done by dividing the sum of the interests by the difference,
				# so that values that are closer are higher-valued
				rom = tempAdults[i].calculateRomanticInterest(tempAdults[j])
				recipRom = tempAdults[j].calculateRomanticInterest(tempAdults[i])
				mutualRom = (rom + recipRom)/max(0.00001, abs(rom-recipRom))
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

			# Create a family for these adults
			tempFamily = Family()
			self.families.append(tempFamily)
			tempFamily.addPerson(a1)
			tempFamily.addPerson(a2)

			# Now generate children
			childrenCount = random.randint(0, 3)
			for i in range(childrenCount):
				child = tempFamily.generatePerson([a1, a2], age=random.randint(0, 12*4))
				a1.addChild(child)
				a2.addChild(child)

			# Give enough food for the year
			tempFamily.food = (10*2 + 6*childrenCount)*4

		# Show who's in the community
		print(self)
		# Pass time once without increasing the date
		self.passTime(False)

	def addFamily(self, f):
		self.families.append(f)

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
		# TODO
		# Family pass time (WIP)
		# Harsh winter, other events
		# Social interactions
		# People actions based on final mood and events during social interactions

		if autoDateIncrease:
			self.date += 1

		# update modifiers before everything else, to prevent added modifiers from being
		# immediately decreased in duration
		for p in self.allPeople():
			p.updateModifiers()

		print("\n\n==== {} ====".format(self.dateToString().upper()))
		if self.season() == 3:
			# harsh winter
			if random.randint(1,5) == 1: # TODO hardcoded
				print("The winter is a harsh one")
				self.harshWinter = True
				for p in self.allPeople():
					p.addModifier(12) # add 'cold' modifier
			else:
				self.harshWinter = False

		for f in self.families:
			f.passTime(self.date%4, self.harshWinter)

		for p in self.allPeople(minAge=3*4):
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
						mappedByRapport[i] = p.rapport[i]+1 # +1 to make positive
					else:
						mappedByRapport[i] = 1 # neutral
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
						# TODO: actual interaction
						# TODO hardcoded (loads)
						if p.likes(b) and b.likes(p):
							if random.randint(1,3) == 1:
								# deep talk
								p.updateRapport(b, 0.9)
								b.updateRapport(p, 0.6)
								p.interactionLog.append("I had a deep talk with {}".format(b.printableFullName()))
								b.interactionLog.append("{} had a deep talk with me".format(p.printableFullName()))
							else:
								# quick chat
								p.updateRapport(b, 0.03)
								b.updateRapport(p, 0.02)
								p.interactionLog.append("I had a quick chat with {}".format(b.printableFullName()))
								b.interactionLog.append("{} had a quick chat with me".format(p.printableFullName()))
						else:
							p.updateRapport(b, -0.05)
							b.updateRapport(p, -0.05)
							p.interactionLog.append("I had an argument with {}".format(b.printableFullName()))
							b.interactionLog.append("{} had an argument with me".format(p.printableFullName()))
						break
					else:
						currentNum += mappedByRapport[b]


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