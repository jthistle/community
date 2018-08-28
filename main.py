#!/usr/bin/env python3

import random, math, moods
from person import Person
from family import Family
from community import Community
from tests import Tests

def main():
	testRun = Tests()
	#testRun.runRomTests()

	community = Community()

	while True:
		input()
		community.date += 1
		community.passTime()

	

	'''f1= Family()
	#community.addFamily(f1)

	f1.generatePerson([None, None], age=80, gender="male")
	f1.generatePerson([None, None], age=80, gender="female")

	print(str(f1))

	print(str(f1.getPerson(0)))
	print(str(f1.getPerson(1)))

	print(f1.getPerson(0).calculateCap(f1.getPerson(1)))
	print(f1.getPerson(0).explainCap(f1.getPerson(1)))
	#print(f1.getPerson(0).calculateCap(f1.getPerson(1)))
	#print(f1.getPerson(1).calculateCap(f1.getPerson(0)))
	#print(f1.getPerson(0).calculateRomanticInterest(f1.getPerson(1)))
	#print(f1.getPerson(1).calculateRomanticInterest(f1.getPerson(0)))'''

if __name__ == "__main__":
	main()