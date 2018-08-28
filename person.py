#!/usr/bin/env python3

import random, math
from namegen import NameGen
from moods import MOODS

nameGen = NameGen()

class Person:
	'''
	Base person class
	Uses the OCEANPI trait model, an adapted version of the OCEAN/Big Five model

	Openness
	Conscientiousness
	Extrovertion
	Agreeableness
	Neuroticism
	aPpearance
	Intelligence
	'''
	__genders = ["male", "female"]
	__attributes = ["o", "c", "e", "a", "n", "p", "i"]

	def __init__(self, parents, partner=None, gender="", age=0, surname=""):
		self.parents = parents
		self.children = []
		self.partner = partner

		if gender != "":
			if gender == "male":
				self.gender = "male"
			else:
				self.gender = "female"
		else:
			self.gender = random.choice(self.__genders)

		self.age = age 	# stored in seasons

		self.attributes = {}

		# Attributes are based on a truncated gaussian distribution
		for attr in self.__attributes:
			self.attributes[attr] = min(1, max(0, round(random.gauss(0.5, 0.2), 2)))

		if surname != "":
			self.name = [nameGen.first(self.gender), surname]
		else:
			self.name = nameGen.full(self.gender)

		self.modifiers = {}	# mood modifiers

		self.rapport = {}	# stores rapport with other people

	def passTime(self):
		# TODO
		# Add function to perform actions based on mood or events?
		self.age += 1
		self.updateModifiers()

	def calculateCap(self, b):
		'''
		Calculates the Coefficient of appreciation

		~ denotes negative values should be truncated
		Formula is:
		(Ab + Ab*(Eb-Ea)~ - 0.5*Nb*(1-Aa))~
		-----------------------------------
			 0.5*(|Oa-Ob|+|Ca-Cb|)+0.1
		'''

		cap = max(0, (b.attributes["a"] \
			+ b.attributes["a"]*max(0, (b.attributes["e"]-self.attributes["e"])) \
			- 0.5*b.attributes["n"]*(1-self.attributes["a"]) +1
			))

		cap = cap / (0.5*(abs(self.attributes["a"]-b.attributes["a"])+\
			abs(self.attributes["c"]-b.attributes["c"])) +0.1)

		return cap

	def calculateRomanticInterest(self, b):
		'''
		Romantic interest is a function of the Cap, inflated or deflated based on appearance
		'''
		rom = self.calculateCap(b) * (0.5*(b.attributes["p"]-self.attributes["p"])+1)
		return rom

	def firstName(self):
		return self.name[0]
	def surname(self):
		return self.name[1]
	def printableFullName(self):
		return "{} {}".format(self.name[0], self.name[1])
	def setSurname(self, s):
		self.name[1] = s
	def regenerateFirstName(self):
		self.name[0] = nameGen.first(self.gender)

	def getMood(self):
		tempMood = self.baseMood()
		for m in self.modifiers.keys():
			tempMood += self.modifiers[m][1]
		return max(-2, min(2, tempMood))

	def father(self):
		if parents[0] == None:
			return False
		elif parents[0].gender == "male":
			return parents[0]
		else:
			return parents[1]
	def mother(self):
		if parents[0] == None:
			return False
		elif parents[0].gender == "female":
			return parents[0]
		else:
			return parents[1]

	def baseMood(self):
		return self.attributes["e"] - self.attributes["n"]
	def addModifier(self, moodId):
		''' 
		This will also overwrite any set modifier
		'''
		self.modifiers[moodId] = MOODS[moodId]

	def updateModifiers(self):
		'''
		Decreases duration by 1 for every mood, and cleans up
		'''
		for mId in self.modifiers.keys():
			self.modifiers[mId][2] -= 1
			if self.modifiers[mId][2] == 0:
				del self.modifiers[mId]

	def emotionality(self):
		'''
		How prone to feeling emotions, positive or negative, a person is
		'''
		return 0.5*(self.attributes["e"] + self.attributes["n"])
	def politicalOrientation(self):
		'''
		Left = 1
		Right = 0
		'''
		return 0.5*(self.attributes["o"] + self.attributes["a"])
	def sociopathy(self):
		'''
		>0.9 = Sociopath
		>0.6 = Sociopathic tendencies
		'''
		return 0.5*(self.attributes["c"] - self.attributes["a"] + 1)

	def isChild(self):
		if self.age < 16*4:
			return True
		return False

	def getAttr(self, letter):
		return self.attributes[letter]

	def ageToString(self):
		return "{} year(s), {} season(s)".format(self.age//4, self.age%4)

	def attributesToString(self):
		toReturn = ""
		for attr in self.attributes.keys():
			toReturn = toReturn+("\n{}: {}".format(attr, self.attributes[attr]))
		return toReturn

	def attributesAsDescription(self):
		toReturn = []
		for attr in self.attributes.keys():
			val = self.attributes[attr]
			if attr == "o":
				if val > 0.8:
					toReturn.append("{} is very inventive and creative".format(self.firstName()))
				elif val > 0.5:
					toReturn.append("{} is fairly inventive and creative".format(self.firstName()))
				elif val > 0.2:
					toReturn.append("{} is fairly consistent and cautious".format(self.firstName()))
				else:
					toReturn.append("{} is very consistent and cautious".format(self.firstName()))
			elif attr == "c":
				if val > 0.8:
					toReturn.append("{} is very efficient and organised".format(self.firstName()))
				elif val > 0.5:
					toReturn.append("{} is fairly efficient and organised".format(self.firstName()))
				elif val > 0.2:
					toReturn.append("{} is fairly easy-going and careless".format(self.firstName()))
				else:
					toReturn.append("{} is very easy-going and careless".format(self.firstName()))
			elif attr == "e":
				if val > 0.8:
					toReturn.append("{} is very outgoing and energetic".format(self.firstName()))
				elif val > 0.5:
					toReturn.append("{} is fairly outgoing and energetic".format(self.firstName()))
				elif val > 0.2:
					toReturn.append("{} is fairly solitary and reserved".format(self.firstName()))
				else:
					toReturn.append("{} is very solitary and reserved".format(self.firstName()))
			elif attr == "a":
				if val > 0.8:
					toReturn.append("{} is very friendly and compassionate".format(self.firstName()))
				elif val > 0.5:
					toReturn.append("{} is fairly friendly and compassionate".format(self.firstName()))
				elif val > 0.2:
					toReturn.append("{} is fairly antagonistic and detatched".format(self.firstName()))
				else:
					toReturn.append("{} is very antagonistic and detatched".format(self.firstName()))
			elif attr == "n":
				if val > 0.8:
					toReturn.append("{} is very insecure and nervous".format(self.firstName()))
				elif val > 0.5:
					toReturn.append("{} is fairly insecure and nervous".format(self.firstName()))
				elif val > 0.2:
					toReturn.append("{} is fairly secure and confident".format(self.firstName()))
				else:
					toReturn.append("{} is very secure and confident".format(self.firstName()))
			elif attr == "p":
				if val > 0.8:
					toReturn.append("{} is very good-looking".format(self.firstName()))
				elif val > 0.5:
					toReturn.append("{} is fairly good-looking".format(self.firstName()))
				elif val > 0.2:
					toReturn.append("{} isn't very good-looking".format(self.firstName()))
				else:
					toReturn.append("{} isn't good-looking".format(self.firstName()))
			elif attr == "i":
				if val > 0.8:
					toReturn.append("{} is very intelligent".format(self.firstName()))
				elif val > 0.5:
					toReturn.append("{} is fairly intelligent".format(self.firstName()))
				elif val > 0.2:
					toReturn.append("{} isn't very intelligent".format(self.firstName()))
				else:
					toReturn.append("{} isn't intelligent".format(self.firstName()))

		return "\n".join(toReturn)

	def otherAttributesAsDescription(self):
		bm = self.baseMood()
		em = self.emotionality()
		po = self.politicalOrientation()
		so = self.sociopathy()

		toReturn = []
		if em > 0.8:
			toReturn.append("{} is very emotional".format(self.firstName()))
		elif em > 0.5:
			toReturn.append("{} is fairly emotional".format(self.firstName()))
		elif em > 0.2:
			toReturn.append("{} is fairly unemotional".format(self.firstName()))
		else:
			toReturn.append("{} is very unemotional".format(self.firstName()))

		if po > 0.8:
			toReturn.append("{} is very left-wing".format(self.firstName()))
		elif po > 0.5:
			toReturn.append("{} is centre-left-wing".format(self.firstName()))
		elif po > 0.2:
			toReturn.append("{} is centre-right-wing".format(self.firstName()))
		else:
			toReturn.append("{} is very right-wing".format(self.firstName()))

		if so > 0.9:
			toReturn.append("{} is a sociopath".format(self.firstName()))
		elif so > 0.6:
			toReturn.append("{} shows sociopathic tendencies".format(self.firstName()))
		else:
			toReturn.append("{} isn't a sociopath".format(self.firstName()))

		if bm > 0.6:
			toReturn.append("{} is an optimist".format(self.firstName()))
		elif bm > 0.0:
			toReturn.append("{} is fairly optimistic".format(self.firstName()))
		elif bm > -0.6:
			toReturn.append("{} is fairly pessimistic".format(self.firstName()))
		else:
			toReturn.append("{} is very pessimistic".format(self.firstName()))

		return "\n".join(toReturn)


	def __str__(self):
		toReturn = []
		toReturn.append("{} {}".format(self.name[0], self.name[1]))
		toReturn.append("Aged {}".format(self.ageToString()))
		toReturn.append("Gender {}".format(self.gender))
		toReturn.append("Core attributes\n {}".format(self.attributesAsDescription()))
		toReturn.append("Other attributes\n {}".format(self.otherAttributesAsDescription()))
		toReturn.append("")

		return "\n".join(toReturn)