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
