#!/usr/bin/env python3

import random
import math
from namegen import NameGen
from moods import MOODS
from config import *

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

	__genders = GENDERS
	__attributes = ATTRIBUTES
	__capCutoff = CAP_CUTOFF
	__lifeExpectancy = LIFE_EXPECTANCY

	def __init__(self, parents, family=None, partner=None, gender="", age=0, surname="", married=False):
		self.parents = parents
		self.children = []
		self.partner = partner
		self.age = age 				# stored in seasons
		self.married = married
		self.alive = True
		self.family = family
		self.eventLog = []			# stores text log of interactions
		self.modifiers = {}			# mood modifiers
		self.rapport = {}			# stores rapport with other people
		self.timeWithPartner = 0
		self.keyEvents = []
		self.deathData = {}

		# very fatalistic, but generates a lifetime for a person
		self.lifetime = random.gauss(self.__lifeExpectancy, LIFE_EXPECTANCY_SD)

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

	def breakUp(self):
		if self.partner is not None:
			self.log("I broke up with {}".format(self.partner.printableFullName()))
			self.partner.log("{} broke up with me".format(self.printableFullName()))
			self.family.community.log("{} broke up with {}".format(
				self.printableFullName(), self.partner.printableFullName()))
			self.addModifier(6)
			self.partner.addModifier(6)
			self.timeWithPartner = 0
			self.partner.timeWithPartner = 0
			self.partner.partner = None
			self.partner = None

	def marryPartner(self):
		if self.partner is not None and not self.married:
			self.log("I married {}".format(self.partner.printableFullName()))
			self.partner.log("I married {}".format(self.printableFullName()))
			self.family.community.log("{} married {}".format(
				self.printableFullName(), self.partner.printableFullName()))
			self.married = True
			self.partner.married = True
			self.addModifier(5)
			self.partner.addModifier(5)

			# Create new family
			# The family name is not carried over to prevent confusion
			newFamily = self.family.community.newFamily()
			self.family.removePerson(self)
			self.partner.family.removePerson(self.partner)

			self.family = newFamily
			self.partner.family = newFamily
			newFamily.addPerson(self)
			newFamily.addPerson(self.partner)

			self.logKeyEvent("married {}".format(self.partner.firstName()))
			self.partner.logKeyEvent("married {}".format(self.firstName()))

			self.family.community.log("The couple have taken the new name of the {} family of {}s".format(
				self.family.familyName, self.family.profession))

	def passTime(self):
		self.age += 1
		self.log("== {} ==".format(self.ageToString()))

		if self.partner is not None and not self.married:
			self.timeWithPartner += 1
			# decide whether to break up
			if self.timeWithPartner >= 2 and not self.romanticallyLikes(self.partner):
				self.breakUp()

			if self.partner is not None:
				# Since conscientiousness reflects spontaneity, modify the base time by the highest value
				minMarriageTime = BASE_MARRIAGE_MIN_TIME * (0.5 + max(self.getAttr("c"), self.partner.getAttr("c")))
				if self.timeWithPartner >= minMarriageTime and self.age >= MARRIAGE_MIN_AGE and\
					self.partner.age >= MARRIAGE_MIN_AGE:
					# Get married! Other marraige conditions can go here in the future
					if self.romanticallyLikes(self.partner) and self.partner.romanticallyLikes(self):
						self.marryPartner()
		else:
			self.timeWithPartner = 0

		if self.married and self.partner.alive:
			# Decide whether to have baby, but only if married, and both people
			# still are attracted to each other. Chance of baby decreases with number of
			# children.
			# probably a bad way to find lowest age
			if len(self.children) > 0:
				lowestAge = self.children[-1].age
			else:
				lowestAge = 4

			if lowestAge > 3 and\
				len(self.children) < BABY_MAX_AMOUNT and\
				self.romanticallyLikes(self.partner) and self.partner.romanticallyLikes(self):
				if random.randint(1, BASE_BABY_CHANCE*(len(self.children)+1)) == 1:
					child = self.family.generatePerson([self, self.partner])
					if self.gender == "female":
						self.log("I gave birth to {}".format(child.firstName()))
						self.family.community.log("{} gave birth to {}".format(self.printableFullName(),
							child.firstName()))
					else:
						self.log("My wife gave birth to {}".format(child.firstName()))
						self.family.community.log("{} gave birth to {}".format(self.partner.printableFullName(),
							child.firstName()))
					self.children.append(child)
					self.partner.children.append(child)
					self.addModifier(15)
					self.partner.addModifier(15)

		# life expectancy is calculated by another random truncated gaussian distribution
		if self.age > self.lifetime:
			self.die()
			return True

		if self.partner is None:
			friends = self.countFriends()
			if friends[0] <= MAX_ARMY_BEST_FRIENDS and friends[1] <= MAX_ARMY_FRIENDS and\
				self.age >= MIN_ARMY_AGE and self.age <= MAX_ARMY_AGE and self.gender == "male":
				# Whether someone wants to join the army is a function of conscientiousness
				multiplier = 10
				armyChance = multiplier*(BASE_ARMY_CHANCE - self.getAttr("c")*2)
				if random.randint(1, math.ceil(armyChance)) <= multiplier:
					self.log("I left the community to join the army")
					self.family.community.log("{} has left the community to join the army at the age of {}".format(
						self.printableFullName(), self.ageToString()))
					self.family.removePerson(self)

		# mood level at which someone will commit suicide is currently
		# TODO Could be a function of something in future?
		suicideLevel = SUICIDE_MIN_MOOD_LEVEL
		if self.getMood() <= suicideLevel and not self.isChild():
			self.family.community.log("{} attempted suicide".format(self.firstName()))
			self.log("I attempted suicide")
			self.die()  # TODO - maybe not every time
		elif self.getMood() <= -1.3:
			self.log("I'm feeling very bad")
		elif self.getMood() > 1.3:
			self.log("I'm feeling really good")
		elif self.getMood() > 2:
			self.log("I'm feeling euphoric")

		# Rapport decays towards 0 by a set value per season
		for r in self.rapport.keys():
			if self.rapport[r] >= RAPPORT_DECAY:
				self.rapport[r] -= RAPPORT_DECAY
			elif self.rapport[r] <= -RAPPORT_DECAY:
				self.rapport[r] += RAPPORT_DECAY
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

		cap = max(0, (b.getAttr("a") +
			b.getAttr("a")*max(0, (b.getAttr("e")-self.getAttr("e"))) -
			0.5*b.getAttr("n")*(1-self.getAttr("a"))+1))

		cap = cap / (0.5*(abs(self.getAttr("o")-b.getAttr("o")) +
			abs(self.getAttr("c")-b.getAttr("c")))+0.1)

		return cap

	def calculateRomanticInterest(self, b):
		'''
		Romantic interest is a function of the Cap, inflated or deflated based on appearance
		'''
		rom = self.calculateCap(b) * (0.5*(b.getAttr("p")-self.getAttr("p"))+1)
		return rom

	def romanticInterestThreshold(self, b):
		'''
		The romantic interest threshold is a function of extroversion, agreableness,
		and rapport.
		'''
		thresh = 5 - 0.5*(self.getAttr("a")+self.getAttr("e")) - 2*self.rapport[b]
		return thresh

	def likes(self, b):
		if self.calculateCap(b) >= self.__capCutoff:
			return True
		return False

	def romanticallyLikes(self, b):
		if self.calculateRomanticInterest(b) >= self.romanticInterestThreshold(b):
			return True
		return False

	def isRelative(self, b):
		if b in self.family.people:
			return True
		if b in self.children:
			return True
		if self.parents[0] is not None:
			geneticFamily = self.father().family
			if b in geneticFamily.people:
				return True
			siblings = self.father().children
			if b in siblings:
				return True

	def firstName(self):
		return self.name[0]

	def surname(self):
		return self.name[1]

	def printableFullName(self):
		return "{} {}".format(self.name[0], self.name[1])

	def setFirstName(self, s):
		self.name[0] = s

	def setSurname(self, s):
		self.name[1] = s

	def regenerateFirstName(self):
		self.name[0] = nameGen.first(self.gender)

	def die(self):
		# TODO: other things, I guess
		self.alive = False
		self.deathData["date"] = self.family.community.date
		bestFriends = []
		for p in self.rapport.keys():
			if not self.isRelative(p):
				if self.rapport[p] >= BEST_FRIEND_THRESHOLD:
					bestFriends.append(p)
		self.deathData["bestFriends"] = bestFriends
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
				return "{} hasn't got on well with {}".format(n1, n2)
			elif rp >= -0.8:
				return "{} dislikes {}".format(n1, n2)
			elif rp >= -1:
				return "{} despises {}".format(n1, n2)
		else:
			return "{} has never talked to {}".format(n1, n2)

	def friends(self):
		bestFriends = []
		friends = []

		# sort by rapport
		sortedRapportKeys = sorted(list(self.rapport.keys()), key=lambda x: self.rapport[x], reverse=True)
		for p in sortedRapportKeys:
			if self.isRelative(p) or not p.alive:
				continue
			if self.rapport[p] >= BEST_FRIEND_THRESHOLD:
				bestFriends.append(p)
			elif self.rapport[p] >= FRIEND_THRESHOLD:
				friends.append(p)

		toReturn = []
		if len(bestFriends) > 0:
			toReturn.append("Best friends with: ".format(self.firstName()) +
				", ".join([x.printableFullName() for x in bestFriends]))
		else:
			if len(friends) > 0:
				toReturn.append("{} has no best friends".format(self.firstName()))
		if len(friends) > 0:
			toReturn.append("Friends with: ".format(self.firstName()) +
				", ".join([x.printableFullName() for x in friends]))
		elif len(bestFriends) == 0:
				toReturn.append("{} has no friends".format(self.firstName()))

		return ". ".join(toReturn)

	def countFriends(self):
		'''
		Returns [friends, best friends]
		'''
		bestFriends = 0
		friends = 0

		for p in self.rapport.keys():
			if self.isRelative(p) or not p.alive:
				continue
			if self.rapport[p] >= BEST_FRIEND_THRESHOLD:
				bestFriends += 1
			elif self.rapport[p] >= FRIEND_THRESHOLD:
				friends += 1

		return [bestFriends, friends]

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

	def moodReasons(self):
		toReturn = []
		if len(self.modifiers) == 0:
			return "for no reason in particular"

		for m in self.modifiers:
			toReturn.append(self.modifiers[m][0].lower())

		return "for these reasons: "+", ".join(toReturn)

	def addChild(self, p):
		if p not in self.children:
			self.children.append(p)

	def father(self):
		if self.parents[0] is None:
			return False
		elif self.parents[0].gender == "male":
			return self.parents[0]
		else:
			return self.parents[1]

	def mother(self):
		if self.parents[0] is None:
			return False
		elif self.parents[0].gender == "female":
			return self.parents[0]
		else:
			return self.parents[1]

	def baseMood(self):
		return self.getAttr("e") - self.getAttr("n")

	def addModifier(self, moodId):
		'''
		This will also overwrite any set modifier
		'''
		self.modifiers[moodId] = MOODS[moodId].copy()  # lists are mutable, so copy

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
		'''
		Returns attribute, but with age differences applied.
		Openness, extroversion and neuroticism decrease over time,
		but conscientiousness and agreeableness increase.
		'''
		mod = 0
		if letter in ["o", "e", "n"]:
			mod = -ATTRIBUTE_CHANGE * (self.age/ATTRIBUTE_CHANGE_AGE)
		elif letter in ["c", "a"]:
			mod = ATTRIBUTE_CHANGE * (self.age/ATTRIBUTE_CHANGE_AGE)

		return min(1, max(0, self.attributes[letter]+mod))

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
			dislikes.append("{} is quite quiet compared to {}".format(n2, n1))

		neuroNegative = 0.5*b.getAttr("n")*(1-self.getAttr("a"))
		if neuroNegative >= 0.25 and self.getAttr("a") < 0.5:
			dislikes.append("{} is quite insecure - something that {} particularly hates".format(n2, n1))
		elif neuroNegative >= 0.25 and self.getAttr("a") >= 0.5:
			dislikes.append("{} is insecure enough to bother even {}".format(n2, n1))
		elif neuroNegative >= 0 and self.getAttr("a") >= 0.5 and b.getAttr("n") >= 0.5:
			likes.append("{} may be a bit insecure, but this doesn't really bother {}".format(n2, n1))
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
			toReturn = "Overall, {} likes {} because {}.".format(n1, n2, likes[0])
			for i in range(1, len(likes)):
				toReturn = toReturn + " {}.".format(capitalizePreserve(likes[i]))

			if len(dislikes) > 0:
				toReturn = toReturn + " {} does dislike {} slightly because {}.".format(n1, n2, dislikes[0])
				for i in range(1, len(dislikes)):
					toReturn = toReturn + " {}.".format(capitalizePreserve(dislikes[i]))

				toReturn = toReturn + " Overall, though, {} likes {}.".format(n1, n2)
		else:
			if len(dislikes) > 0:
				toReturn = "Overall, {} dislikes {} because {}.".format(n1, n2, dislikes[0])
				for i in range(1, len(dislikes)):
					toReturn = toReturn + " {}.".format(capitalizePreserve(dislikes[i]))
			else:
				# weird 'feature' where someone will dislike someone, even though no one
				# value that should increase dislike is very high
				toReturn = "Overall, {} dislikes {}. No reason why, they just do.".format(n1, n2)

			if len(likes) > 0:
				toReturn = toReturn + " {} does like {} slightly because {}.".format(n1, n2, likes[0])
				for i in range(1, len(likes)):
					toReturn = toReturn + " {}.".format(capitalizePreserve(likes[i]))

				toReturn = toReturn + " Overall, though, {} dislikes {}.".format(n1, n2)

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
					toReturn.append("very inventive and creative")
				elif val > 0.5:
					toReturn.append("fairly inventive and creative")
				elif val > 0.2:
					toReturn.append("fairly consistent and cautious")
				else:
					toReturn.append("very consistent and cautious")
			elif attr == "c":
				if val > 0.8:
					toReturn.append("very efficient and organised")
				elif val > 0.5:
					toReturn.append("fairly efficient and organised")
				elif val > 0.2:
					toReturn.append("fairly easy-going and careless")
				else:
					toReturn.append("very easy-going and careless")
			elif attr == "e":
				if val > 0.8:
					toReturn.append("very outgoing and energetic")
				elif val > 0.5:
					toReturn.append("fairly outgoing and energetic")
				elif val > 0.2:
					toReturn.append("fairly solitary and reserved")
				else:
					toReturn.append("very solitary and reserved")
			elif attr == "a":
				if val > 0.8:
					toReturn.append("very friendly and compassionate")
				elif val > 0.5:
					toReturn.append("fairly friendly and compassionate")
				elif val > 0.2:
					toReturn.append("fairly antagonistic and detatched")
				else:
					toReturn.append("very antagonistic and detatched")
			elif attr == "n":
				if val > 0.8:
					toReturn.append("very insecure and nervous")
				elif val > 0.5:
					toReturn.append("fairly insecure and nervous")
				elif val > 0.2:
					toReturn.append("fairly secure and confident")
				else:
					toReturn.append("very secure and confident")
			elif attr == "p":
				if val > 0.8:
					toReturn.append("very good-looking")
				elif val > 0.5:
					toReturn.append("fairly good-looking")
				elif val > 0.2:
					toReturn.append("not very good-looking")
				else:
					toReturn.append("not good-looking")
			elif attr == "i":
				if val > 0.8:
					toReturn.append("very intelligent")
				elif val > 0.5:
					toReturn.append("fairly intelligent")
				elif val > 0.2:
					toReturn.append("not very intelligent")
				else:
					toReturn.append("not intelligent")

		strToReturn = "{} is {} and {}.".format(self.firstName(), ", ".join(toReturn[:len(toReturn)-1]),
			toReturn[len(toReturn)-1])
		return strToReturn

	def otherAttributesAsDescription(self):
		bm = self.baseMood()
		em = self.emotionality()
		po = self.politicalOrientation()
		so = self.sociopathy()

		toReturn = []
		if em > 0.8:
			toReturn.append("very emotional")
		elif em > 0.5:
			toReturn.append("fairly emotional")
		elif em > 0.2:
			toReturn.append("fairly unemotional")
		else:
			toReturn.append("very unemotional")

		if po > 0.8:
			toReturn.append("very left-wing")
		elif po > 0.5:
			toReturn.append("centre-left-wing")
		elif po > 0.2:
			toReturn.append("centre-right-wing")
		else:
			toReturn.append("very right-wing")

		if so > 0.9:
			toReturn.append("a sociopath")
		elif so > 0.6:
			toReturn.append("shows sociopathic tendencies")
		else:
			toReturn.append("not a sociopath")

		if bm > 0.6:
			toReturn.append("an optimist")
		elif bm > 0.0:
			toReturn.append("fairly optimistic")
		elif bm > -0.6:
			toReturn.append("fairly pessimistic")
		else:
			toReturn.append("very pessimistic")

		strToReturn = "{} is also {} and {}.".format(self.firstName(), ", ".join(toReturn[:len(toReturn)-1]),
			toReturn[len(toReturn)-1])

		return strToReturn

	def getLastInteractions(self, n):
		toReturn = []
		for i in range(min(len(self.eventLog), n)):
			toReturn.append(self.eventLog[i])
		return "\n".join(toReturn)

	def compareTo(self, b):
		'''
		Returns a comparison of the two people, using explainCap, and
		rapportStatus
		'''
		toReturn = []
		toReturn.append("{} {}.".format(self.explainCap(b), capitalizePreserve(self.rapportStatus(b))))
		toReturn.append("{} {}.".format(b.explainCap(self), capitalizePreserve(b.rapportStatus(self))))
		return "\n".join(toReturn)

	def log(self, s):
		self.eventLog.append(s)

	def logKeyEvent(self, s):
		self.keyEvents.append([self.family.community.date, s])

	def dateToString(self, d):
		year = BASE_YEAR + d//4
		season = self.family.community.seasonToString(d%4)
		return "{} {}".format(season, year)

	def inspect(self):
		'''
		Returns some text for the GUI inspector
		'''
		toReturn = []
		toReturn.append("== {} ==".format(self.printableFullName()))
		if self.alive:
			toReturn.append("Aged {}".format(self.ageToString()))
			toReturn.append("Gender {}".format(self.gender))
			toReturn.append(self.attributesAsDescription()+" "+self.otherAttributesAsDescription())
			toReturn.append("{} is feeling {} {}.".format(self.firstName(), self.oneWordMood(), self.moodReasons()))
			toReturn.append("{}.".format(self.friends()))
			if self.married:
				if self.partner.alive:
					toReturn.append("{} is married to {}.".format(self.firstName(), self.partner.printableFullName()))
				else:
					toReturn.append("{} is a widow(er).".format(self.firstName()))
			elif self.partner is not None:
				toReturn.append("{} has been going out with {} for {} seasons.".format(
					self.firstName(), self.partner.printableFullName(), self.timeWithPartner))
		else:
			deathDate = self.deathData["date"]
			toReturn.append("RIP: {} - {}".format(self.dateToString(deathDate-self.age), self.dateToString(deathDate)))
			toReturn.append("Gender {}".format(self.gender))

			if len(self.keyEvents) > 0:
				toAdd = ""
				for e in self.keyEvents:
					toAdd = toAdd + "In {}, {} {}. ".format(self.dateToString(e[0]), self.firstName(), e[1])
				toReturn.append(toAdd)

			toReturn.append((self.attributesAsDescription()+" "+self.otherAttributesAsDescription()).replace(
				" is ", " was "))
			if self.married:
				toReturn.append("{} was married to {}.".format(self.firstName(), self.partner.printableFullName()))
			toReturn.append("{} was a parent to {} child(ren)".format(self.firstName(), len(self.children)))

			bfs = self.deathData["bestFriends"]
			if len(bfs) == 0:
				toReturn.append("{} was not missed by anyone outside their family.".format(self.firstName()))
			else:
				toAdd = "{} was missed by ".format(self.firstName())
				toAdd = toAdd + ", ".join([f.printableFullName() for f in bfs][:-1])
				if len(bfs) == 1:
					toAdd = toAdd + "{}.".format(bfs[0].printableFullName())
				else:
					toAdd = toAdd + ", and {}.".format(bfs[-1].printableFullName())
				toReturn.append(toAdd)

		return "\n".join(toReturn)

	def __str__(self):
		toReturn = []
		toReturn.append("=== {} {}".format(self.name[0], self.name[1]))
		toReturn.append("=== Aged {}".format(self.ageToString()))
		toReturn.append("=== Gender {}".format(self.gender))
		toReturn.append("=== Core attributes\n{}".format(self.attributesAsDescription()))
		toReturn.append("=== Other attributes\n{}".format(self.otherAttributesAsDescription()))
		toReturn.append("=== Last five interactions\n{}".format(self.getLastInteractions(5)))
		toReturn.append("=== Friends\n{}".format(self.friends()))
		toReturn.append("")

		return "\n".join(toReturn)


def capitalizePreserve(s):
	'A helper function that capitalizes the first letter, and preserves other capitals'
	return s[0].capitalize()+s[1:]
