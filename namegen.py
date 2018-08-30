#!/usr/bin/env python3

import names


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
