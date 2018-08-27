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
		self.date = 2 # SET TO 0
		self.harshWinter = False

		# generate 3 families, each with 2 adults and randomly 0-3 children
		# Do this by generating 6 adults (aged 20-40) and matching them based on romantic interest
		# Highest mutual romantic interest = pair
		tempAdults = []
		for i in range(6):
			gender = "female"
			if i%2 == 0:
				gender = "male"

			tempAdults.append(Person([None, None], gender=gender, age=random.randint(20*4,40*4)))

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

			# Give enough food for the year
			tempFamily.food = (10*2 + 6*childrenCount)*4

		# Pass time once without increasing the date
		self.passTime()

	def addFamily(self, f):
		self.families.append(f)

	def allPeople(self):
		tempP = []
		for f in self.families:
			for p in f.people:
				tempP.append(p)

		return tempP

	def passTime(self):
		# TODO
		# Family pass time (WIP)
		# Harsh winter, other events
		# Social interactions
		# People actions based on final mood and events during social interactions
		
		print(self.dateToString())
		for f in self.families:
			f.passTime(self.date%4, self.harshWinter)

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