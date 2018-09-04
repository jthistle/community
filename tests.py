#!/usr/bin/env python3

import random
import math
import csv
from person import Person
from family import Family
from community import Community


class Tests:
	def __init__(self):
		None

	def run(self):
		c = Community()
		f1 = Family(c)
		f2 = Family(c)
		c.addFamily(f1)
		c.addFamily(f2)
		c.removeFamily(f2)
		f2 = c.newFamily()
		f1ByInd = c.getFamilyByIndex(0)

		p1 = Person([None, None], gender="male", family=f1)
		p2 = Person([None, None], gender="female", family=f1)
		p1.partner = p2
		p2.partner = p1
		p1.marryPartner()

		f1.addPerson(p1)
		f1.addPerson(p2)
		p3 = f1.generatePerson([p1, p2])
		p3ByInd = f1.getPerson(2)
		p1.addChild(p3)
		p2.addChild(p3)

		p4 = f1.generatePerson([p1, p2])
		f1.removePerson(p4)
		f1.addPerson(p4)
		f1.removePersonByIndex(3)

		p5 = Person([None, None], gender="male", family=f1)
		p6 = Person([None, None], gender="female", family=f1)
		p5.partner = p6
		p6.partner = p5
		p5.updateRapport(p6, -0.5)
		p5.breakUp()

		p5.calculateCap(p6)
		p5.likes(p6)
		p5.calculateRomanticInterest(p6)
		p5.romanticallyLikes(p6)

		p1.isRelative(p3)

		p1.firstName()
		p1.surname()
		p1.printableFullName()
		p1.setFirstName("test")
		p1.setSurname("test")
		p1.regenerateFirstName()

		p1.rapportStatus(p2)
		p1.friends()
		p1.countFriends()
		p1.getMood()
		p1.oneWordMood()
		p1.moodReasons()
		p1.father()
		p1.mother()
		p1.baseMood()
		p1.addModifier(2)
		p1.emotionality()
		p1.politicalOrientation()
		p1.sociopathy()
		p1.isChild()
		p1.getAttr("o")
		p1.explainCap(p2)
		p1.ageToString()
		p1.attributesToString()
		p1.attributesAsDescription()
		p1.otherAttributesAsDescription()
		p1.getLastInteractions(5)
		p1.compareTo(p2)
		p1.logKeyEvent("test")
		p1.inspect()
		p1.die()

		c.log("test message")
		f1.log("test message")

		allPeople = c.allPeople()

		c.passTime()
		c.graveyard()

	# LEGACY TESTS
	def runCapTests(self):
		f1 = Family(None)
		with open("data.csv", "w", newline="") as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(["Cap"])
			for i in range(10000):
				f1.generatePerson(None, age=80, gender="male")
				f1.generatePerson(None, age=80, gender="female")

				val1 = f1.getPerson(0).calculateCap(f1.getPerson(1))
				val2 = f1.getPerson(1).calculateCap(f1.getPerson(0))
				writer.writerow([val1])
				writer.writerow([val2])

				f1.removePersonByIndex(1)
				f1.removePersonByIndex(0)

	def runRomTests(self):
		f1 = Family(None)
		with open("data.csv", "w", newline="") as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(["Rom"])
			for i in range(10000):
				f1.generatePerson(None, age=80, gender="male")
				f1.generatePerson(None, age=80, gender="female")

				val1 = f1.getPerson(0).calculateRomanticInterest(f1.getPerson(1))
				val2 = f1.getPerson(1).calculateRomanticInterest(f1.getPerson(0))
				writer.writerow([val1])
				writer.writerow([val2])

				f1.removePersonByIndex(1)
				f1.removePersonByIndex(0)

	def runCapVsRomTests(self):
		community = Community()

		f1 = Family()
		community.addFamily(f1)

		with open("data.csv", "w", newline="") as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(["Cap", "Rom"])
			for i in range(10000):
				f1.generatePerson(None, age=80, gender="male")
				f1.generatePerson(None, age=80, gender="female")

				val1 = f1.getPerson(0).calculateCap(f1.getPerson(1))
				val2 = f1.getPerson(1).calculateCap(f1.getPerson(0))
				val3 = f1.getPerson(0).calculateRomanticInterest(f1.getPerson(1))
				val4 = f1.getPerson(1).calculateRomanticInterest(f1.getPerson(0))
				writer.writerow([val1, val3])
				writer.writerow([val2, val4])

				f1.removePersonByIndex(1)
				f1.removePersonByIndex(0)


if __name__ == "__main__":
	t = Tests()
	t.run()
