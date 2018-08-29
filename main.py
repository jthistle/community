#!/usr/bin/env python3

import random, math, moods, sys
from person import Person
from family import Family
from community import Community
from tests import Tests

def takeMenuInput(min, max):
	'Min - max is inclusive'
	choice = max+1
	while choice > max:
		try:
			choice = int(input("> "))
		except Exception as e:
			if e == EOFError or e == KeyboardInterrupt:
				endProgram()
			else:
				print("Must be a number")
	return choice

def endProgram():
	sys.exit()

def main():
	testRun = Tests()
	#testRun.runRomTests()

	community = Community()

	while True:
		print("")
		# rudimentary menu system
		for f in community.families:
			print(str(f)+"\n")

		choice = 1
		comparison = False
		while choice != 0:
			print("0: continue")
			for i in range(len(community.families)):
				print("{}: {} family".format(i+1, community.families[i].familyName))

			choice = takeMenuInput(0, len(community.families))
			if choice == 0:
				None
			else:
				f = community.families[choice-1]
				people = f.people
				
				choice2 = 1
				while choice2 != 0:
					print("\n==== The {} Family ====".format(f.familyName))
					print("0: exit")
					for i in range(len(people)):
						print("{}: {}".format(i+1, people[i].firstName()))
					choice2 = takeMenuInput(0, len(people))
					if choice2 != 0:
						p = people[choice2-1]
						if comparison != False:
							print(comparison.compareTo(p))
							comparison = False
						else:
							print("0: view\n1: compare")
							choice3 = takeMenuInput(0,1)
							if choice3 == 0:
								print(str(p))
							else:
								comparison = p
								choice2 = 0 # leave the family loop

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