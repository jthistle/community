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

	# LEGACY
	def runCapTests(self):
		f1 = Family(None)
		with open("data.csv", "w", newline="") as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(["Cap"])
			for i in range(10000):
				f1.generatePerson(None, None, age=80, gender="male")
				f1.generatePerson(None, None, age=80, gender="female")

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
				f1.generatePerson(None, None, age=80, gender="male")
				f1.generatePerson(None, None, age=80, gender="female")

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
				f1.generatePerson(None, None, age=80, gender="male")
				f1.generatePerson(None, None, age=80, gender="female")

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
