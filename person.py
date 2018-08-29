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

	# TODO hardcoded: place in config file
	__genders = ["male", "female"]
	__attributes = ["o", "c", "e", "a", "n", "p", "i"]
	__capCutoff = 3.5
	__lifeExpectancy = 40*4

	def __init__(self, parents, family=None, partner=None, gender="", age=0, surname="", married=False):
		self.parents = parents
		self.children = []
		self.partner = partner
		self.age = age 				# stored in seasons
		self.married = married
		self.alive = True
		self.family = family
		self.interactionLog = []	# stores text log of interactions
		self.modifiers = {}			# mood modifiers
		self.rapport = {}			# stores rapport with other people
		
		# very fatalistic, but generates a lifetime for a person
		self.lifetime = random.gauss(self.__lifeExpectancy, 5*4) # TODO hardcoded

		if gender != "":
			if gender == "male":
				self.gender = "male"
			else:
				self.gender = "female"
		else:
			self.gender = random.choice(self.__genders)

		self.attributes = {}
		# Attributes are based on a truncated gaussian distribution
		for attr in self.__attributes:
			self.attributes[attr] = min(1, max(0, round(random.gauss(0.5, 0.2), 2)))

		if surname != "":
			self.name = [nameGen.first(self.gender), surname]
		else:
			self.name = nameGen.full(self.gender)

	def passTime(self):
		# TODO
		# Add function to perform actions based on mood or events?
		self.age += 1

		# life expectancy is calculated by another random truncated gaussian distribution
		if self.age > self.lifetime:
			self.die()
			return True

		# mood level at which someone will commit suicide is currently
		# hardcoded. Could be a function of something in future?
		# was previouslymin(1.9, 2 - 0.5*self.getAttr("n"))
		suicideLevel = -1.9
		if self.getMood() <= suicideLevel and not self.isChild():
			print("{} attempted suicide".format(self.firstName()))
			self.die() # TODO - maybe not every time
		elif self.getMood() <= -1.5:
			print("{} is feeling very bad".format(self.firstName()))
		elif self.getMood() > 1.5:
			print("{} is feeling really good".format(self.firstName()))
		elif self.getMood() > 2:
			print("{} is feeling euphoric".format(self.firstName()))

		# Rapport decays towards 0 by 0.05 per season
		for r in self.rapport.keys():
			if self.rapport[r] >= 0.05:
				self.rapport[r] -= 0.05
			elif self.rapport[r] <= -0.05:
				self.rapport[r] += 0.05
			else:
				self.rapport[r] = 0
		
	def updateRapport(self, p, diff):
		'''
		Updates rapport with person p by diff amount
		Rapport is a number ranging from -0.95 to 1
		'''
		if p in self.rapport.keys():
			self.rapport[p] += diff
		else:
			self.rapport[p] = diff

		# Why is -0.95 the min? So that there ALWAYS is a chance of interaction.
		self.rapport[p] = max(-0.95, min(1, self.rapport[p]))

	def calculateCap(self, b):
		'''
		Calculates the Coefficient of appreciation

		~ denotes negative values should be truncated
		Formula is:
		(Ab + Ab*(Eb-Ea)~ - 0.5*Nb*(1-Aa))~
		-----------------------------------
			 0.5*(|Oa-Ob|+|Ca-Cb|)+0.1
		'''

		cap = max(0, (b.getAttr("a") \
			+ b.getAttr("a")*max(0, (b.getAttr("e")-self.getAttr("e"))) \
			- 0.5*b.getAttr("n")*(1-self.getAttr("a")) +1
			))

		cap = cap / (0.5*(abs(self.getAttr("a")-b.getAttr("a"))+\
			abs(self.getAttr("c")-b.getAttr("c"))) +0.1)

		return cap

	def calculateRomanticInterest(self, b):
		'''
		Romantic interest is a function of the Cap, inflated or deflated based on appearance
		'''
		rom = self.calculateCap(b) * (0.5*(b.getAttr("p")-self.getAttr("p"))+1)
		return rom

	def likes(self, b):
		if self.calculateCap(b) >= self.__capCutoff:
			return True
		return False

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

	def die(self):
		# TODO: other things, I guess
		self.alive = False
		print("{} died at the age of {}".format(self.printableFullName(), self.ageToString()))
		self.family.memberDied(self)

	def rapportStatus(self, b):
		'''
		Returns rapport as a third-person opinion sentence
		'''
		n1 = self.firstName()
		n2 = b.firstName()
		if b in self.rapport.keys():
			rp = self.rapport[b]
			if rp >= 1:
				return "{} knows {} better than anyone".format(n1, n2)
			elif rp >= 0.8:
				return "{} gets on great with {}".format(n1, n2)
			elif rp >= 0.5:
				return "{} is friends with {}".format(n1, n2)
			elif rp >= 0.2:
				return "{} has chatted with {}".format(n1, n2)
			elif rp >= 0.0:
				return "{} knows {}".format(n1, n2)
			elif rp >= -0.2:
				return "{} has chatted with {}".format(n1, n2)
			elif rp >= -0.5:
				return "{} doesn't really like {}".format(n1, n2)
			elif rp >= -0.8:
				return "{} hasn't got on well with {}".format(n1, n2)
			elif rp >= -1:
				return "{} despises {}".format(n1, n2)
		else:
			return "{} has never talked to {}".format(n1, n2)

	def getMood(self):
		tempMood = self.baseMood()
		for m in self.modifiers.keys():
			tempMood += self.modifiers[m][1]
		return max(-2, min(2, tempMood))

	def oneWordMood(self):
		if self.getMood() == 2:
			return "euphoric"
		elif self.getMood() >= 1.5:
			return "great"
		elif self.getMood() >= 1:
			return "good"
		elif self.getMood() >= 0.5:
			return "not bad"
		elif self.getMood() >= 0:
			return "average"
		elif self.getMood() >= -0.5:
			return "a bit down"
		elif self.getMood() >= -1:
			return "blue"
		elif self.getMood() >= -1.5:
			return "bad"
		elif self.getMood() >= -2:
			return "suicidal"

	def addChild(self, p):
		if p not in self.children:
			self.children.append(p)
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
		return self.getAttr("e") - self.getAttr("n")
	def addModifier(self, moodId):
		''' 
		This will also overwrite any set modifier
		'''
		self.modifiers[moodId] = MOODS[moodId].copy() # lists are mutable, so copy

	def updateModifiers(self):
		'''
		Decreases duration by 1 for every mood, and cleans up
		'''
		tempKeys = list(self.modifiers.keys()).copy()
		for mId in tempKeys:
			self.modifiers[mId][2] -= 1
			if self.modifiers[mId][2] == 0:
				del self.modifiers[mId]

	def emotionality(self):
		'''
		How prone to feeling emotions, positive or negative, a person is
		'''
		return 0.5*(self.getAttr("e") + self.getAttr("n"))
	def politicalOrientation(self):
		'''
		Left = 1
		Right = 0
		'''
		return 0.5*(self.getAttr("o") + self.getAttr("a"))
	def sociopathy(self):
		'''
		>0.9 = Sociopath
		>0.6 = Sociopathic tendencies
		'''
		return 0.5*(self.getAttr("c") - self.getAttr("a") + 1)

	def isChild(self):
		if self.age < 16*4:
			return True
		return False

	def getAttr(self, letter):
		return self.attributes[letter]

	def explainCap(self, b):
		'''
		Explains why a cap was generated. Welcome to format hell.

		~ denotes negative values should be truncated
		Formula is, for reference:
		(Ab + Ab*(Eb-Ea)~ - 0.5*Nb*(1-Aa))~
		-----------------------------------
			 0.5*(|Oa-Ob|+|Ca-Cb|)+0.1
		'''
		n1 = self.firstName()
		n2 = b.firstName()
		cap = self.calculateCap(b)

		likes = []
		dislikes = []
		if b.getAttr("a") >= 0.8:
			likes.append("{} is extremely friendly".format(n2))
		elif b.getAttr("a") >= 0.5:
			likes.append("{} is fairly friendly".format(n2))
		elif b.getAttr("a") >= 0.2:
			dislikes.append("{} is quite argumentative".format(n2))
		else:
			dislikes.append("{} is very argumentative".format(n2))

		extroDiff = max(0, b.getAttr("e") - self.getAttr("e"))
		if extroDiff >= 0.5 and b.getAttr("a") >= 0.5:
			likes.append("{} talks so much more - and is nice when they do".format(n2))
		elif extroDiff >= 0.5 and b.getAttr("a") < 0.5:
			dislikes.append("{} talks so much more, but isn't very nice".format(n2))
		elif extroDiff > 0:
			likes.append("{} is a bit more extroverted".format(n2))
		elif extroDiff == 0:
			dislikes.append("{} is quite quiet compared to {}".format(n2,n1))

		neuroNegative = 0.5*b.getAttr("n")*(1-self.getAttr("a"))
		if neuroNegative >= 0.25 and self.getAttr("a") < 0.5:
			dislikes.append("{} is quite insecure - something that {} particularly hates".format(n2,n1))
		elif neuroNegative >= 0.25 and self.getAttr("a") >= 0.5:
			dislikes.append("{} is insecure enough to bother even {}".format(n2,n1))
		elif neuroNegative >= 0 and self.getAttr("a") >= 0.5 and b.getAttr("n") >= 0.5:
			likes.append("{} may be a bit insecure, but this doesn't really bother {}".format(n2,n1))
		else:
			likes.append("{} is quite secure and confident".format(n2))

		openDiff = abs(self.getAttr("o")-b.getAttr("o"))
		if openDiff < 0.1 and self.getAttr("o") >= 0.5:
			likes.append("they are just as creative and curious as each other")
		elif openDiff < 0.1 and self.getAttr("o") < 0.5:
			likes.append("they are just as cautious and consistent as each other")
		elif openDiff <= 0.25 and self.getAttr("o") >= 0.5:
			likes.append("they share some feelings of creativity")
		elif openDiff <= 0.25 and self.getAttr("o") >= 0.5:
			likes.append("they share some feelings of consistency")
		elif openDiff >= 0.75:
			dislikes.append("{} is very different in terms of openness".format(n2))

		conDiff = abs(self.getAttr("o")-b.getAttr("o"))
		if conDiff < 0.1 and self.getAttr("o") >= 0.5:
			likes.append("they are just as efficient and organised as each other")
		elif conDiff < 0.1 and self.getAttr("o") < 0.5:
			likes.append("they are just as easy-going and spontaneous as each other")
		elif conDiff <= 0.25 and self.getAttr("o") >= 0.5:
			likes.append("they share some feelings of efficiency")
		elif conDiff <= 0.25 and self.getAttr("o") >= 0.5:
			likes.append("they share some feelings of spontaneity")
		elif conDiff >= 0.75:
			dislikes.append("{} is very different in terms of conscientiousness".format(n2))

		if cap >= self.__capCutoff:
			toReturn = "Overall, {} likes {} because {}.".format(n1,n2,likes[0])
			for i in range(1, len(likes)):
				toReturn = toReturn + " {}.".format(capitalizePreserve(likes[i]))

			if len(dislikes) > 0:
				toReturn = toReturn + " {} does dislike {} slightly because {}.".format(n1,n2,dislikes[0])
				for i in range(1, len(dislikes)):
					toReturn = toReturn + " {}.".format(capitalizePreserve(dislikes[i]))

				toReturn = toReturn + " Overall, though, {} likes {}.".format(n1,n2)
		else:
			if len(dislikes) > 0:
				toReturn = "Overall, {} dislikes {} because {}.".format(n1,n2,dislikes[0])
				for i in range(1, len(dislikes)):
					toReturn = toReturn + " {}.".format(capitalizePreserve(dislikes[i]))
			else:
				# weird 'feature' where someone will dislike someone, even though no one
				# value that should increase dislike is very high
				toReturn = "Overall, {} dislikes {}. No reason why, they just do.".format(n1,n2)

			if len(likes) > 0:
				toReturn = toReturn + " {} does like {} slightly because {}.".format(n1,n2,likes[0])
				for i in range(1, len(likes)):
					toReturn = toReturn + " {}.".format(capitalizePreserve(likes[i]))

				toReturn = toReturn + " Overall, though, {} dislikes {}.".format(n1,n2)

		return toReturn

		

	def ageToString(self):
		return "{} year(s), {} season(s)".format(self.age//4, self.age%4)

	def attributesToString(self):
		toReturn = ""
		for attr in self.attributes.keys():
			toReturn = toReturn+("\n{}: {}".format(attr, self.getAttr(attr)))
		return toReturn

	def attributesAsDescription(self):
		toReturn = []
		for attr in self.attributes.keys():
			val = self.getAttr(attr)
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

	def getLastInteractions(self, n):
		toReturn = []
		for i in range(min(len(self.interactionLog), n)):
			toReturn.append(self.interactionLog[i])
		return "\n".join(toReturn)

	def compareTo(self, b):
		'''
		Returns a comparison of the two people, using explainCap, and
		rapportStatus TODO
		'''
		toReturn = []
		toReturn.append("{} {}.".format(self.explainCap(b), capitalizePreserve(self.rapportStatus(b))))
		toReturn.append("{} {}.".format(b.explainCap(self), capitalizePreserve(b.rapportStatus(self))))
		return "\n".join(toReturn)

	def __str__(self):
		toReturn = []
		toReturn.append("{} {}".format(self.name[0], self.name[1]))
		toReturn.append("Aged {}".format(self.ageToString()))
		toReturn.append("Gender {}".format(self.gender))
		toReturn.append("Core attributes\n {}".format(self.attributesAsDescription()))
		toReturn.append("Other attributes\n {}".format(self.otherAttributesAsDescription()))
		toReturn.append("Last five interactions\n {}".format(self.getLastInteractions(5)))
		toReturn.append("")

		return "\n".join(toReturn)

def capitalizePreserve(s):
	'A helper function that capitalizes the first letter, and preserves other capitals'
	return s[0].capitalize()+s[1:]