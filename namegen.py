#!/usr/bin/env python3

import names
import random


class NameGen():
	def __init__(self):
		None

	def full(self, gender):
		return [self.first(gender), self.last()]

	def first(self, gender):
		if gender == "male":
			return names.get_first_name(gender="male")
		else:
			return names.get_first_name(gender="female")

	def last(self):
		return names.get_last_name()

	def factionName(self):
		formatStrs = ["The Legion of {}", "The Brothers of {}", "The Band of {}", "{}'s warriors", "The {} Squadron"]
		return random.choice(formatStrs).format(names.get_last_name())

	def workTitle(self):
		formatStrs = [("On the {} {}", ("adj", "noun")), ("The {}", ("noun",)), ("{}", ("noun",)),
			("{} and {}", ("noun", "noun")), ("{}", ("adj",)), ("{} {}", ("adj", "noun")),
			("{} {} {} the {}", ("adj", "noun", "prep", "noun"))]

		nouns = ["cheese", "origin", "time", "thought", "love", "house", "music", "look", "sight", "taste", "meaning",
			"creation", "result", "smell", "view", "flow", "note", "rhythm", "brush", "bush", "sun", "star", "system",
			"moon", "dog", "cat", "mouse", "father", "mother", "sea", "army", "fight", "flight", "ride", "explosion",
			"sunset", "water", "freedom", "lake", "mountains", "valley", "river", "stream", "cove", "cliff",
			"tune", "escape"]

		adjectives = ["cheesy", "long", "happy", "sad", "terrible", "frightening", "red", "orange", "yellow", "green",
			"blue", "indigo", "purple", "violet", "turquoise", "royal", "soft", "hard", "sharp", "massive", "giant",
			"understandable", "mournful", "crazed", "lonely", "quiet", "loud", "explosive", "unobtainable",
			"celestial", "ethereal", "still", "raging", "ragged", "burning", "rocky", "sandy", "clear", "opaque",
			"cloudy", "overcast", "wintery", "excited", "violent", "short", "momentary"]

		prepositions = ["on", "in", "by", "under", "over", "through", "near", "behind", "in front of",
			"opposite"]

		titleData = random.choice(formatStrs)
		titleToReturn = titleData[0]
		for el in titleData[1]:
			parts = [x+"{}" for x in titleToReturn.split("{}")[:-1]]
			if el == "noun":
				parts[0] = parts[0].format(random.choice(nouns))
			elif el == "adj":
				parts[0] = parts[0].format(random.choice(adjectives))
			elif el == "prep":
				parts[0] = parts[0].format(random.choice(prepositions))
			titleToReturn = "".join(parts)

		return self.titleCap(titleToReturn)

	def titleCap(self, s):
		nonCap = ["on", "in", "by", "under", "over", "through", "near", "behind", "front",
			"opposite", "the", "a", "an", "and", "in", "of"]

		toReturn = s.split(" ")
		for i in range(len(toReturn)):
			if toReturn[i] not in nonCap:
				toReturn[i] = toReturn[i].capitalize()

		toReturn[0] = toReturn[0].capitalize()

		return " ".join(toReturn)
