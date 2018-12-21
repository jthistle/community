#!/usr/bin/env python3

import random
import math
from namegen import NameGen
from family import Family
from person import Person
from moods import MOODS
from config import *


class Community:
	'Base community class'
	__baseYear = BASE_YEAR

	def __init__(self):
		self.families = []asdasdasdas
		self.deadFamilies = []
		self.date = 0  # SET TO 0 IF NOT
		self.harshWinter = False
		self.eventLog = []
		self.mayor = None
		self.mayorFamily = None
		self.mayorTime = 0
		self.mayorTerms = 0
		# In the format ["mayor name", start date, end date]
		self.mayorHistory = []
		# In the format ["title", "author name", date]
		self.greatWorks = []

		# generate 3 families, each with 2 adults and randomly 0-3 children
		# Do this by generating 6 adults (aged 20-40) and matching them based on romantic interest
		# Highest mutual romantic interest = pair
		tempAdults = []
		for i in range(6):
			gender = "female"
			if i % 2 == 0:
				gender = "male"

			tempAdults.append(Person([None, None], gender=gender, age=random.randint(18*4, 25*4), married=True))

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

			a1.updateRapport(a2, START_RELATIVE_RAPPORT)
			a2.updateRapport(a1, START_RELATIVE_RAPPORT)

			# Create a family for these adults
			tempFamily = Family(self)
			self.families.append(tempFamily)
			tempFamily.addPerson(a1)
			tempFamily.addPerson(a2)

			# Now generate children
			childrenCount = random.randint(2, 4)
			for i in range(childrenCount):
				child = tempFamily.generatePerson([a1, a2], age=random.randint(0, START_CHILDREN_MAX_AGE))
				a1.addChild(child)
				a2.addChild(child)
				# Make sure to set a base rapport
				a1.updateRapport(child, START_RELATIVE_RAPPORT)
				a2.updateRapport(child, START_RELATIVE_RAPPORT)
				child.updateRapport(a1, START_RELATIVE_RAPPORT)
				child.updateRapport(a2, START_RELATIVE_RAPPORT)

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
		for f in self.deadFamilies:
			for p in f.deadPeople:
				tempP.append(p)

		return tempP

	def startMayorTime(self, p):
		self.mayorHistory.append([p.printableFullName(), self.date, -1])

	def endMayorTime(self):
		self.mayorHistory[-1][2] = self.date

	def mayorTotalTime(self):
		years = (self.mayorTerms * MAYOR_TERM_LENGTH)//4
		years += self.mayorTime//4
		return years

	def passTime(self, autoDateIncrease=True):
		'''
		Passes time, updating things in this order:
			1. Increase date
			2. Update moods (remove expired modifiers)
			3. Decide season events
			4. Pass time in families (subroutine).
			5. Social interactions including on-the-fly mood changes
		'''

		if autoDateIncrease:
			self.date += 1
			self.mayorTime += 1

		for p in self.allPeople():
			if autoDateIncrease:
				p.age += 1
			p.log("== {} ==".format(p.ageToString()))

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

		if self.season() == ELECTION_SEASON and (self.mayorTime >= MAYOR_TERM_LENGTH or
			self.mayor is None):
			self.log("An election is occuring")

			# Work out who can stand for election
			# Max 3 candidates are chosen
			# Everyone recieves a suitability rating, based on their extroversion + agreeableness

			allP = self.allPeople()
			candidates = []
			lowestRating = -1
			for p in allP:
				rating = p.mayoralSuitability()
				if (rating > lowestRating or len(candidates) < 3) and p.age >= MIN_MAYOR_AGE:
					candidates.append(p)
					candidates = sorted(candidates, key=lambda x: x.mayoralSuitability(), reverse=True)
					if len(candidates) > 3:
						del candidates[-1]
					lowestRating = candidates[-1].mayoralSuitability()

			if len(candidates) < 3:
				self.log("There are not enough eligible candidates to hold an election.")
			else:
				# We now have the top three candidates.
				# Commence voting!
				self.log("The candidates standing are: {}, {} and {}".format(candidates[0].printableFullName(),
					candidates[1].printableFullName(), candidates[2].printableFullName()))

				votes = {c: 0 for c in candidates}
				for p in allP:
					if p.age >= MIN_VOTING_AGE:
						lowestDiff = 1
						chosen = None
						for c in candidates:
							if p == c:
								# Always choose yourself if possible
								lowestDiff = -1000
								chosen = p
							else:
								orientationDiff = abs(p.politicalOrientation()-c.politicalOrientation())
								# Modify by rapport
								orientationDiff -= p.getRapport(c)*RAPPORT_VOTING_MODIFIER
								if orientationDiff < lowestDiff:
									chosen = c
									lowestDiff = orientationDiff

						if chosen is not None:
							votes[chosen] += 1
							p.log("I voted for {}".format(chosen.printableFullName()))

				candidatesByVotes = sorted(votes.keys(), key=lambda x: votes[x], reverse=True)

				if votes[candidatesByVotes[0]] == votes[candidatesByVotes[1]]:
					# Deal with a hung election
					self.log("{} and {} are tied on {} votes".format(candidatesByVotes[0].printableFullName(),
						candidatesByVotes[1].printableFullName(), votes[candidatesByVotes[0]]))

					if self.mayor is not None:
						self.log("{} leaves office after {} years as mayor, due to a hung election".format(
							self.mayor.printableFullName(), self.mayorTotalTime()))
						self.mayor.log("I left mayoral office after a hung election".format(self.mayor.printableFullName()))
						self.mayor.logKeyEvent("left mayoral office")

						self.mayor.isMayor = False
						self.mayor = None
						self.mayorFamily = None
						self.mayorTime = 0
						self.mayorTerms = 0
						# Set end date for this person
						self.endMayorTime()
					else:
						self.log("No mayor has been elected.")
				else:
					# We have a winner! It doesn't need to be a majority, just the highest vote count.
					winner = candidatesByVotes[0]

					# Add lost election modifiers
					candidatesByVotes[1].addModifier(19)
					candidatesByVotes[2].addModifier(19)

					if self.mayor is not winner:
						self.log("{} wins with {} votes".format(winner.printableFullName(), votes[winner]))
						winner.logKeyEvent("became mayor")
						winner.log("I became mayor")
						winner.addModifier(18)
					else:
						self.log("{} continues in office with {} votes".format(winner.printableFullName(), votes[winner]))
						self.mayorTerms += 1

					self.log("2nd: {} with {} votes".format(candidatesByVotes[1].printableFullName(),
						votes[candidatesByVotes[1]]))
					self.log("3rd: {} with {} votes".format(candidatesByVotes[2].printableFullName(),
						votes[candidatesByVotes[2]]))

					if self.mayor is not None:
						if self.mayor is not winner:
							self.log("{} leaves office after {} years as mayor".format(self.mayor.printableFullName(),
								self.mayorTotalTime()))
							self.mayor.log("I left mayoral office, beaten by {}".format(winner.printableFullName()))
							self.mayor.logKeyEvent("left mayoral office")
							# Set end date for this person
							self.endMayorTime()
						self.mayor.isMayor = False

					if self.mayor is not winner:
						# Set start date for this person
						self.startMayorTime(winner)
						self.mayorTerms = 0

					# Actally set the mayor variables
					self.mayor = winner
					self.mayorTime = 0
					self.mayorFamily = self.mayor.family
					self.mayor.isMayor = True

		# Decide whether to trigger 'invading army' event
		if len(self.families) > COMMUNITY_FAMILY_LIMIT and COMMUNITY_FAMILY_LIMIT != 0:
			namegen = NameGen()
			factionName = namegen.factionName()
			self.log("An invading army, {}, is passing through the community".format(factionName))
			for i in range(ATTACK_KILL_AMOUNT):
				fInd = random.randint(0, len(self.families)-1)
				f = self.families[fInd]
				self.log("The {} family is wiped out by the attack".format(f.familyName))
				for p in f.people:
					p.die()
				self.removeFamily(f)
				self.deadFamilies.append(f)

		# Decide whether to trigger 'family joins event'
		if len(self.families) < COMMUNITY_FAMILY_MIN:
			for i in range(COMMUNITY_FAMILY_JOIN):
				# generate family
				tempFam = Family(self)
				p1 = Person([None, None], gender="male", age=random.randint(18*4, 25*4), married=True)
				p2 = Person([None, None], gender="female", age=random.randint(18*4, 25*4), married=True)
				p1.partner = p2
				p2.partner = p1
				p1.updateRapport(p2, START_RELATIVE_RAPPORT)
				p2.updateRapport(p1, START_RELATIVE_RAPPORT)
				tempFam.addPerson(p1)
				tempFam.addPerson(p2)

				for j in range(random.randint(2, 4)):
					child = tempFam.generatePerson([p1, p2], age=random.randint(0, START_CHILDREN_MAX_AGE))
					p1.children.append(child)
					p2.children.append(child)
					p1.updateRapport(child, START_RELATIVE_RAPPORT)
					p2.updateRapport(child, START_RELATIVE_RAPPORT)

				self.addFamily(tempFam)
				self.log("The {} family, a family of {}s has joined the community".format(tempFam.familyName, tempFam.profession))

		for f in self.families:
			if len(f.people) == 0:
				# everyone's died
				self.log("The old house of the {} family is left deserted".format(f.familyName))
				self.removeFamily(f)
				self.deadFamilies.append(f)
			else:
				f.passTime(self.date%4, self.harshWinter)

		for p in self.allPeople(minAge=START_INTERACTION_MIN_AGE):
			# A person interacts with 0-10 people per day, based on extroversion
			interactions = math.ceil(p.getAttr("e")*10)
			if p.isMayor:
				interactions = math.ceil(interactions * MAYOR_INTERACTIONS_MOD)
			for i in range(math.ceil(p.getAttr("e")*10)):
				# This next bit works by mapping by rapport. Basically,
				# a person will be more likely to initiate social interactions
				# with someone who they have more rapport with.
				mappedByRapport = {}
				totalRapport = 0
				for i in self.allPeople():
					if i == p:
						continue

					mappedByRapport[i] = p.getRapport(i)+1  # +1 to make positive

					# Younger people will want to talk to people of their own age.
					# So, decrease the mapping by a number based on age.
					# How does the formula work? Black magic and duct tape.
					# Of course, this doesn't apply to family.
					# This assumes that there is no age prejudice above 16 - TODO?
					if i not in p.family.people:
						addition = (8 - abs((i.age-p.age)//4)) * max(0, ((16*4-p.age)/16*4))
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
							if p.isRelative(b):
								famMod = FAMILY_ARGUMENT_MOD
							else:
								famMod = 1

							# Decide whether to initiate a fight
							fought = False
							if p.getRapport(b) <= FIGHT_MAX_RAPPORT and p.age > FIGHT_MIN_AGE:
								chance = max(2, FIGHT_BASE_CHANCE - (p.getAttr("e")*2+p.getAttr("n")*2))

								if random.uniform(0, chance) <= 1:
									p.updateRapport(b, FIGHT_RAPPORT_GAIN*INTERACTED_WITH_MOD*famMod)
									b.updateRapport(p, FIGHT_RAPPORT_GAIN*famMod)
									p.log("I started a fight with {}".format(b.printableFullName()))
									b.log("{} started a fight with me".format(p.printableFullName()))
									if random.randint(1, FIGHT_DEATH_CHANCE) == 1:
										if random.randint(1, 2) == 1:
											self.log("{} killed {} after {} started a fight".format(
												p.printableFullName(), b.printableFullName(), p.firstName()))
											b.die()
											if p.sociopathy() >= SOCIOPATH_THRESH:
												p.log("I killed {}, but feel no remorse.".format(b.firstName()))
											else:
												p.log("I killed {}. I feel terrible.".format(b.firstName()))
												p.addModifier(21)
										else:
											self.log("{} killed {} in self-defence after {} started a fight".format(
												b.printableFullName(), p.printableFullName(), p.firstName()))
											p.die()
											if b.sociopathy() >= SOCIOPATH_THRESH:
												b.log("I killed {} in self-defence, but feel no remorse.".format(p.firstName()))
											else:
												b.log("I killed {} in self-defence.".format(p.firstName()))
												b.addModifier(22)
									fought = True

							if not fought:
								if b.age > MIN_ARGUMENT_AGE and p.age > MIN_ARGUMENT_AGE:
									p.updateRapport(b, ARGUMENT_RAPPORT_GAIN*INTERACTED_WITH_MOD*famMod)
									b.updateRapport(p, ARGUMENT_RAPPORT_GAIN*famMod)
									p.log("I had an argument with {}".format(b.printableFullName()))
									b.log("{} had an argument with me".format(p.printableFullName()))
								else:
									p.updateRapport(b, ANGRY_LOOK_RAPPORT_GAIN*INTERACTED_WITH_MOD*famMod)
									b.updateRapport(p, ANGRY_LOOK_RAPPORT_GAIN*famMod)
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
