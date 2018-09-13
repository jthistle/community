#!/usr/bin/env python3

from tkinter import filedialog
from tkinter import *
import random
import math
import sys
import os
import pickle
from person import Person
from family import Family
from community import Community
from tests import Tests
from config import *


class Application(Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.pack()
		self.createWidgets()
		self.selectedFamily = None
		self.selectedPerson = None
		self.lastInspected = None
		self.viewMode = "inspect"
		self.comparePerson = None

		self.community = Community()
		self.updateWidgets()

	def createWidgets(self):
		'''
		Creates widgets. Hell awaits you.
		'''
		self.btnFrame = Frame()
		self.btnFrame.pack(fill=X)

		self.passTimeBtn = Button(self.btnFrame, text="Pass time", command=self.passTime)
		self.passTimeBtn.grid(row=0, column=0, sticky=E+W)
		self.saveBtn = Button(self.btnFrame, text="Save", command=self.save)
		self.saveBtn.grid(row=0, column=1, sticky=E+W)
		self.loadBtn = Button(self.btnFrame, text="Load", command=self.load)
		self.loadBtn.grid(row=0, column=2, sticky=E+W)
		self.exitBtn = Button(self.btnFrame, text="Exit", command=root.destroy)
		self.exitBtn.grid(row=0, column=3, sticky=E+W)
		self.mayorListBtn = Button(self.btnFrame, text="Mayor list", command=self.mayorListWindow)
		self.mayorListBtn.grid(row=0, column=4, sticky=E+W)
		self.mayorListBtn = Button(self.btnFrame, text="Library", command=self.libraryWindow)
		self.mayorListBtn.grid(row=0, column=5, sticky=E+W)
		self.dateLabel = Label(self.btnFrame, text="")
		self.dateLabel.grid(row=0, column=6, sticky=E+W, padx=10)
		self.inspectBtn = Button(self.btnFrame, text="Inspect", command=self.onInspectBtnClick)
		self.inspectBtn.grid(row=0, column=7, sticky=E+W)
		self.compareBtn = Button(self.btnFrame, text="Compare", command=self.onCompareBtnClick)
		self.compareBtn.grid(row=0, column=8, sticky=E+W)
		self.restFrame = Frame()
		self.restFrame.pack(fill=X)
		self.restFrame.grid_columnconfigure(0, minsize=5, weight=0)
		self.restFrame.grid_columnconfigure(1, minsize=5, weight=0)
		self.restFrame.grid_columnconfigure(2, minsize=5, weight=1)

		self.familiesLabel = Label(self.restFrame, text="Families")
		self.familiesLabel.grid(row=0, column=0, sticky=W)
		self.familiesList = Listbox(self.restFrame, exportselection=False)
		self.familiesList.grid(row=1, column=0, sticky=E+W, padx=5)
		self.familiesList.bind('<<ListboxSelect>>', self.onFamiliesLbChange)

		self.peopleLabel = Label(self.restFrame, text="People")
		self.peopleLabel.grid(row=0, column=1, sticky=W)
		self.peopleList = Listbox(self.restFrame, exportselection=False)
		self.peopleList.grid(row=1, column=1, sticky=E+W, padx=5)
		self.peopleList.bind('<<ListboxSelect>>', self.onPeopleLbChange)

		self.personInfoLabel = Label(self.restFrame, text="Inspector")
		self.personInfoLabel.grid(row=0, column=2, sticky=W)
		self.personInfo = Frame(self.restFrame, borderwidth=2, relief=GROOVE)
		self.personInfo.grid(row=1, column=2, rowspan=3, sticky=N+E+W+S, padx=5)
		self.personInfoText = Label(self.personInfo, text="", anchor=W, justify=LEFT)
		self.personInfoText.config(wraplength=350)
		self.personInfoText.pack(fill=X)
		self.personEvents = Text(self.personInfo, height=10, state=DISABLED)
		self.personEvents.pack(fill=X, padx=5, pady=5, side=BOTTOM)
		self.personEventsLabel = Label(self.personInfo, text="Events")
		self.personEventsLabel.pack(anchor=W, side=BOTTOM)

		self.inspectorBtnFrame = Frame(self.personInfo)
		self.inspectorBtnFrame.pack(anchor=W, side=BOTTOM, padx=5)
		self.fatherBtn = Button(self.inspectorBtnFrame, text="Father", command=self.blank)
		self.fatherBtn.grid(row=0, column=0, sticky=W+E)
		self.fatherBtn.bind('<Button-1>', self.onRelativeButtonClick)
		self.motherBtn = Button(self.inspectorBtnFrame, text="Mother", command=self.blank)
		self.motherBtn.grid(row=0, column=1, sticky=W+E)
		self.motherBtn.bind('<Button-1>', self.onRelativeButtonClick)
		self.partnerBtn = Button(self.inspectorBtnFrame, text="Partner", command=self.blank)
		self.partnerBtn.grid(row=0, column=2, sticky=W+E)
		self.partnerBtn.bind('<Button-1>', self.onRelativeButtonClick)
		self.familyTreeBtn = Button(self.inspectorBtnFrame, text="Family Tree", command=self.familyTreeWindow)
		self.familyTreeBtn.grid(row=0, column=3, sticky=W+E)

		self.eventsLabel = Label(self.restFrame, text="Events")
		self.eventsLabel.grid(row=2, column=0, sticky=W)
		self.eventLog = Text(self.restFrame, width=50, height=19, state=DISABLED)
		self.eventLog.grid(row=3, column=0, columnspan=2, sticky=N+E+W+S, padx=5)

	def updateWidgets(self):
		self.dateLabel.config(text=self.community.dateToString())
		self.familiesList.delete(0, END)
		for f in self.community.families:
			self.familiesList.insert(END, f.familyName)
		self.familiesList.insert(END, "[Graveyard]")
		# Set previous selection
		if self.selectedFamily is not None:
			self.familiesList.selection_set(self.selectedFamily)
		self.updatePeopleList()
		self.updateMainEventLog()
		self.updateInspectorButtons()

		if self.viewMode == "inspect":
			if self.lastInspected == "family":
				self.inspectFamily()
			elif self.lastInspected == "person":
				self.inspectPerson()
			else:
				self.personInfoText.config(text="Select a family to begin")
		elif self.viewMode == "compare":
			if self.comparePerson is None:
				self.writeToInspector("Select a person to compare")

		if self.viewMode == "inspect":
			self.compareBtn.config(relief=RAISED, state=NORMAL)
			self.inspectBtn.config(relief=SUNKEN, state=DISABLED)
		elif self.viewMode == "compare":
			self.compareBtn.config(relief=SUNKEN, state=DISABLED)
			self.inspectBtn.config(relief=RAISED, state=NORMAL)

	def updatePeopleList(self):
		self.peopleList.delete(0, END)
		if self.selectedFamily is not None:
			if self.selectedFamily < len(self.community.families):
				f = self.community.getFamilyByIndex(self.selectedFamily)
				for p in f.people:
					self.peopleList.insert(END, p.firstName())
			else:
				graveyard = self.community.graveyard()
				for p in graveyard:
					self.peopleList.insert(END, p.printableFullName())

		if self.selectedFamily is not None and self.selectedPerson is not None:
			self.peopleList.selection_set(self.selectedPerson)

	def updateInspectorButtons(self):
		partner = self.partnerBtn
		father = self.fatherBtn
		mother = self.motherBtn
		tree = self.familyTreeBtn

		partner.config(state=DISABLED)
		father.config(state=DISABLED)
		mother.config(state=DISABLED)
		tree.config(state=DISABLED)
		if self.selectedPerson is not None:
			p = self.getSelectedPerson()
			if p:
				if p.partner is not None:
					partner.config(state=NORMAL)
				if p.father():
					father.config(state=NORMAL)
				if p.mother():
					mother.config(state=NORMAL)
				tree.config(state=NORMAL)

	def inspectFamily(self):
		self.lastInspected = "family"
		if self.selectedFamily < len(self.community.families):
			f = self.community.getFamilyByIndex(self.selectedFamily)
			self.writeToInspector(f.inspect())
			self.writeInspectorEvents(f.eventLog)
		else:
			self.writeToInspector("== The GRAVEYARD ==\n" +
				"The graveyard holds the memories of all souls that have passed through the community.")
			self.writeInspectorEvents("")

	def inspectPerson(self):
		self.lastInspected = "person"
		if self.selectedPerson is not None:
			self.updateInspectorButtons()
			p = self.getSelectedPerson()
			if p:
				self.writeToInspector(p.inspect())
				self.writeInspectorEvents(p.eventLog)
			else:
				self.writeToInspector("Select a family to begin")
				self.writeInspectorEvents([])

	def comparePeople(self):
		# TODO compare
		p1 = self.comparePerson
		p2 = self.getSelectedPerson()
		self.writeToInspector(p1.compareTo(p2))

	def updateMainEventLog(self):
		self.eventLog.config(state=NORMAL)
		self.eventLog.delete(1.0, END)
		for e in self.community.eventLog:
			self.eventLog.insert(END, e+"\n")
		self.eventLog.see(END)
		self.eventLog.config(state=DISABLED)

	def onFamiliesLbChange(self, evt):
		if len(self.familiesList.curselection()) > 0:
			ind = int(self.familiesList.curselection()[0])
			self.selectedFamily = ind
			self.selectedPerson = None
			self.updatePeopleList()
			self.updateInspectorButtons()

			if self.viewMode == "inspect":
				self.inspectFamily()
			elif self.viewMode == "compare":
				None

	def onPeopleLbChange(self, evt):
		if len(self.peopleList.curselection()) > 0:
			ind = int(self.peopleList.curselection()[0])
			self.selectedPerson = ind

			if self.viewMode == "inspect":
				self.inspectPerson()
			elif self.viewMode == "compare":
				self.comparePeople()

	def onInspectBtnClick(self):
		self.viewMode = "inspect"
		self.comparePerson = None
		self.updateWidgets()

	def onCompareBtnClick(self):
		if self.selectedPerson is not None and self.lastInspected == "person":
			self.viewMode = "compare"
			self.comparePerson = self.getSelectedPerson()
			self.writeToInspector("Select a person to compare to {}".format(self.comparePerson.firstName()))
			self.writeInspectorEvents([])  # clear events panel
		self.updateWidgets()

	def onRelativeButtonClick(self, evt):
		p = self.getSelectedPerson()
		wgt = evt.widget
		if p:
			gyard = self.community.graveyard()
			if wgt == self.fatherBtn and p.father():
				father = p.father()
				if father in gyard:
					self.selectedFamily = len(self.community.families)
					self.selectedPerson = gyard.index(father)
				else:
					self.selectedFamily = self.community.families.index(father.family)
					self.selectedPerson = father.family.people.index(father)
			elif wgt == self.motherBtn and p.mother():
				mother = p.mother()
				if mother in gyard:
					self.selectedFamily = len(self.community.families)
					self.selectedPerson = gyard.index(mother)
				else:
					self.selectedFamily = self.community.families.index(mother.family)
					self.selectedPerson = mother.family.people.index(mother)
			elif wgt == self.partnerBtn and p.partner is not None:
				partner = p.partner
				if partner in gyard:
					self.selectedFamily = len(self.community.families)
					self.selectedPerson = gyard.index(partner)
				else:
					self.selectedFamily = self.community.families.index(partner.family)
					self.selectedPerson = partner.family.people.index(partner)

			self.updateWidgets()

	def writeToInspector(self, s):
		self.personInfoText.config(text=s)

	def writeInspectorEvents(self, events):
		self.personEvents.config(state=NORMAL)
		self.personEvents.delete(1.0, END)
		for e in events:
			self.personEvents.insert(END, e+"\n")
		self.personEvents.see(END)
		self.personEvents.config(state=DISABLED)

	def getSelectedPerson(self):
		if self.selectedFamily is not None and self.selectedPerson is not None:
			if self.selectedFamily < len(self.community.families):
				f = self.community.getFamilyByIndex(self.selectedFamily)
				p = f.getPerson(self.selectedPerson)
				return p
			else:
				# graveyard is selected
				graveyard = self.community.graveyard()
				if self.selectedPerson < len(graveyard):
					p = graveyard[self.selectedPerson]
					return p
				return False

	def passTime(self):
		self.community.passTime()
		self.updateWidgets()

	def save(self):
		cwd = os.path.dirname(os.path.realpath(__file__))
		filename = filedialog.asksaveasfilename(initialdir=cwd, title="Select file",
			filetypes=(("Community save file", "*.cmu"), ("all files", "*.*")))
		if filename:
			with open(filename, "wb") as file:
				try:
					pickle.dump(self.community, file)
				except Exception as e:
					print("An error occurred: {}".format(e))

	def load(self):
		cwd = os.path.dirname(os.path.realpath(__file__))
		filename = filedialog.askopenfilename(initialdir=cwd, title="Select file",
			filetypes=(("Community save file", "*.cmu"), ("all files", "*.*")))
		if filename:
			with open(filename, "rb") as file:
				try:
					tempCom = pickle.load(file)
					if isinstance(tempCom, Community):
						self.community = tempCom
						self.updateWidgets()
					else:
						raise Exception("Could not decode community from save file")
				except Exception as e:
					print("An error occurred: {}".format(e))

	def familyTreeWindow(self):
		w = Toplevel(self)
		w.geometry("600x400")
		w.resizable(0, 0)
		w.wm_attributes("-topmost", 1)
		w.grab_set()
		w.main = FamilyTree(w, self.getSelectedPerson())
		w.main.pack(fill=BOTH)

	def mayorListWindow(self):
		w = Toplevel(self)
		w.geometry("600x600")
		w.resizable(0, 0)
		w.wm_attributes("-topmost", 1)
		w.grab_set()
		w.main = MayorList(w, community=self.community)
		w.main.pack(fill=BOTH)

	def libraryWindow(self):
		w = Toplevel(self)
		w.geometry("600x600")
		w.resizable(0, 0)
		w.wm_attributes("-topmost", 1)
		w.grab_set()
		w.main = Library(w, community=self.community)
		w.main.pack(fill=BOTH)

	def blank(self):
		'Placeholder function'
		None


class FamilyTree(Frame):
	def __init__(self, master=None, person=None):
		super().__init__(master)
		self.master = master
		self.person = person
		self.focus = None
		self.pack()
		self.createWidgets()
		self.updateWidgets()

	def createWidgets(self):
		self.topbarFrame = Frame(self)
		self.topbarFrame.pack(fill=X)
		self.exitBtn = Button(self.topbarFrame, text="Close family tree", command=self.closeWindow)
		self.exitBtn.pack(side=LEFT)

		self.treeFrame = Frame(self)
		self.treeFrame.pack(fill=X)
		self.treeFrame.grid_columnconfigure(0, weight=1)
		self.treeFrame.grid_columnconfigure(1, weight=1)
		self.treeFrame.grid_columnconfigure(2, weight=1)

		self.parentsLabel = Label(self.treeFrame, text="Parents")
		self.parentsLabel.grid(row=0, column=0)
		self.parentsLb = Listbox(self.treeFrame)
		self.parentsLb.grid(row=1, column=0)
		self.parentsLb.bind('<<ListboxSelect>>', self.onParentsLbChange)

		self.siblingsLabel = Label(self.treeFrame, text="Siblings")
		self.siblingsLabel.grid(row=0, column=1)
		self.siblingsLb = Listbox(self.treeFrame, exportselection=False)
		self.siblingsLb.grid(row=1, column=1)
		self.siblingsLb.bind('<<ListboxSelect>>', self.onSiblingsLbChange)

		self.childrenLabel = Label(self.treeFrame, text="Children")
		self.childrenLabel.grid(row=0, column=2)
		self.childrenLb = Listbox(self.treeFrame)
		self.childrenLb.grid(row=1, column=2)
		self.childrenLb.bind('<<ListboxSelect>>', self.onChildrenLbChange)

		self.focusFrame = Frame(self, pady=5, padx=5)
		self.focusFrame.pack(fill=X)
		self.focusBtn = Button(self.focusFrame, text="Focus on selected", command=self.setFocus, padx=5)
		self.focusBtn.grid(row=0, column=0)
		self.focusLabel = Label(self.focusFrame, text="No focus", padx=5)
		self.focusLabel.grid(row=0, column=1)

	def updateWidgets(self):
		'''
		(d.) denotes that someone's dead
		(l.) denotes that they've left to join the army
		'''
		self.parentsLb.delete(0, END)
		if self.person.parents[0] is not None:
			for p in self.person.parents:
				toAppend = ""
				if not p.alive:
					toAppend = toAppend+" (d.)"
				elif p not in p.family.people:
					toAppend = toAppend+" (l.)"
				self.parentsLb.insert(END, p.printableFullName()+toAppend)

		self.siblingsLb.delete(0, END)
		toAppend = ""
		if not self.person.alive:
			toAppend = toAppend+" (d.)"
		elif self.person not in self.person.family.people:
			toAppend = toAppend+" (l.)"
		self.siblingsLb.insert(END, self.person.printableFullName()+toAppend)
		if self.person.married:
			toAppend = ""
			if not self.person.partner.alive:
				toAppend = toAppend+" (d.)"
			elif self.person.partner not in self.person.partner.family.people:
				toAppend = toAppend+" (l.)"
			self.siblingsLb.insert(END, "↳ (m) "+self.person.partner.printableFullName()+toAppend)

		if self.person.parents[0] is not None:
			siblings = self.person.parents[0].children
			for p in siblings:
				if p == self.person:
					continue
				toAppend = ""
				if not p.alive:
					toAppend = toAppend+" (d.)"
				elif p not in p.family.people:
					toAppend = toAppend+" (l.)"
				self.siblingsLb.insert(END, p.printableFullName()+toAppend)
		self.siblingsLb.selection_set(0)

		self.childrenLb.delete(0, END)
		for p in self.person.children:
			toAppend = ""
			if not p.alive:
				toAppend = toAppend+" (d.)"
			elif p not in p.family.people:
				toAppend = toAppend+" (l.)"
			self.childrenLb.insert(END, p.printableFullName()+toAppend)

		if self.focus is not None:
			self.focusLabel.config(text=self.focus.printableFullName())
			# Work out relationships
			# These are done from the POV of the focus
			# e.g [name] is [focus]'s father
			if self.focus is not self.person:
				relationships = []
				# print("debug: Searching for {}".format(self.person.printableFullName()))
				findRel = self.findRelative(self.focus, self.person, 3, toReturn=[])
				if findRel:
					for yVal in findRel.keys():
						yCoord = yVal
						xCoord = findRel[yVal]

						if xCoord == 0:
							if yCoord == -3:
								relationships.append("great grandchild")
							elif yCoord == -2:
								relationships.append("grandchild")
							elif yCoord == -1:
								relationships.append("child")
							elif yCoord == 0:
								relationships.append("sibling")
							elif yCoord == 1:
								relationships.append("parent")
							elif yCoord == 2:
								relationships.append("grandparent")
							elif yCoord == 2:
								relationships.append("great grandparent")
						elif xCoord == 1:
							if yCoord == -3:
								relationships.append("great grand niece/nephew")
							elif yCoord == -2:
								relationships.append("grand niece/nephew")
							elif yCoord == -1:
								relationships.append("niece/nephew")
							elif yCoord == 0:
								relationships.append("first cousin")
							elif yCoord == 1:
								relationships.append("aunt/uncle")
							elif yCoord == 2:
								relationships.append("great aunt/uncle")
							elif yCoord == 3:
								relationships.append("great grand aunt/uncle")
						elif xCoord == 2:
							if yCoord == -3:
								relationships.append("second cousin thrice removed")
							elif yCoord == -2:
								relationships.append("second cousin twice removed")
							elif yCoord == -1:
								relationships.append("second cousin once removed")
							elif yCoord == 0:
								relationships.append("second cousin")
							elif yCoord == 1:
								relationships.append("second cousin once removed")
							elif yCoord == 2:
								relationships.append("second cousin twice removed")
							elif yCoord == 3:
								relationships.append("second cousin thrice removed")
						if len(relationships) == 0:
							self.focusLabel.config(text="No genetic relationship between {} and {}".format(
								self.person.printableFullName(), self.focus.printableFullName()))
						else:
							self.focusLabel.config(text="{} is the {} of {}".format(
								self.person.printableFullName(), ", ".join(relationships), self.focus.printableFullName()))

					# For debug:
					# self.focusLabel.config(text=str(findRel))

	# The plan: use x and y coordinates. Y = how many generations up
	# X = how much separation - 0,0 = sibling, 1,0 = first cousin, 2,0 = second cousin
	def findRelative(self, focus, person, yLimit, currentX=0, currentY=0, goneDown=False,
		goneAcross=False, goneUp=False, firstCall=True, toReturn=[], depth=0):
		DEBUG = False
		if currentY > yLimit or currentY < -yLimit:
			return False
		if focus == person:
			if DEBUG:
				print("="*depth+"debug: **FOUND** {} at {}".format(focus.printableFullName(), str((currentX, currentY))))
			if currentY == 0 and goneAcross and not goneDown:
				toReturn.append((currentX-1, currentY))
			else:
				toReturn.append((currentX, currentY))

		# First: loop through siblings if haven't come from sibling loop
		# Then: go down to children
		# Then: go up to parents if haven't ever gone down
		if focus.parents[0] is not None and not goneAcross:
			siblings = focus.parents[0].children
			for s in siblings:
				if s == focus:
					# s is not a sibling of themself
					continue
				if DEBUG:
					print("="*depth+"debug: going across to {}".format(s.printableFullName()))
				findRel = self.findRelative(s, person, yLimit, currentX+1, currentY, goneDown=goneDown,
					goneAcross=True, goneUp=False, firstCall=False, toReturn=toReturn, depth=depth+1)
				if findRel:
					toReturn = findRel

		# don't go straight back down if we've just come up
		if not goneUp:
			for c in focus.children:
				if DEBUG:
					print("="*depth+"debug: going down to {}".format(c.printableFullName()))
				findRel = self.findRelative(c, person, yLimit, currentX, currentY-1, goneDown=True, goneAcross=False,
					goneUp=False, firstCall=False, toReturn=toReturn, depth=depth+1)
				if findRel:
					toReturn = findRel

		# Don't go up if we've ever gone down, or we've just come from siblings
		if focus.parents[0] is not None and not goneDown and not goneAcross:
			for p in focus.parents:
				if DEBUG:
					print("="*depth+"debug: going up to {}".format(p.printableFullName()))
				findRel = self.findRelative(p, person, yLimit, currentX, currentY+1, goneDown=goneDown, goneAcross=False,
					goneUp=True, firstCall=False, toReturn=toReturn, depth=depth+1)
				if findRel:
					toReturn = findRel

		if firstCall:
			# return only the smallest x val for each y val
			yVals = {}
			for c in toReturn:
				if DEBUG:
					print("debug: Looking at {}".format(str(c)))
				if c[1] in yVals.keys():
					if yVals[c[1]] > c[0]:
						yVals[c[1]] = c[0]
				else:
					yVals[c[1]] = c[0]
			return yVals
		else:
			return toReturn

	def onParentsLbChange(self, evt):
		if len(self.parentsLb.curselection()) > 0:
			ind = int(self.parentsLb.curselection()[0])
			self.person = self.person.parents[ind]
			self.updateWidgets()

	def onSiblingsLbChange(self, evt):
		if len(self.siblingsLb.curselection()) > 0:
			ind = int(self.siblingsLb.curselection()[0])
			indexDiff = 1
			if self.person.married:
				if ind == 1:
					self.person = self.person.partner
				indexDiff = 2

			if ind > indexDiff-1:
				siblings = self.person.parents[0].children.copy()
				siblings.remove(self.person)
				self.person = siblings[ind-indexDiff]
			self.updateWidgets()

	def onChildrenLbChange(self, evt):
		if len(self.childrenLb.curselection()) > 0:
			ind = int(self.childrenLb.curselection()[0])
			self.person = self.person.children[ind]
			self.updateWidgets()

	def setFocus(self):
		self.focus = self.person
		self.updateWidgets()

	def closeWindow(self):
		self.master.grab_release()
		self.master.destroy()


class MayorList(Frame):
	def __init__(self, master=None, community=None):
		super().__init__(master)
		self.master = master
		self.community = community
		self.pack()
		self.createWidgets()
		self.updateWidgets()

	def createWidgets(self):
		self.exitBtn = Button(self, text="Close Mayor list", command=self.closeWindow)
		self.exitBtn.pack(side=TOP)

		self.mayorListbox = Listbox(self, exportselection=False, height=20, width=40)
		self.mayorListbox.pack(side=TOP)

	def updateWidgets(self):
		self.mayorListbox.delete(0, END)
		for i in range(len(self.community.mayorHistory)-1, -1, -1):
			h = self.community.mayorHistory[i]
			name = h[0]
			startDate = h[1]
			endDate = h[2]

			if endDate == -1:
				endDateStr = "present"
			else:
				endDateStr = self.dateToString(endDate)
			startDateStr = self.dateToString(startDate)

			self.mayorListbox.insert(END, "{}: {} - {}".format(name, startDateStr, endDateStr))

	# NOTE: code duplication from Person
	def dateToString(self, d):
		year = BASE_YEAR + d//4
		season = self.community.seasonToString(d%4)
		return "{} {}".format(season, year)

	def closeWindow(self):
		self.master.grab_release()
		self.master.destroy()


class Library(Frame):
	def __init__(self, master=None, community=None):
		super().__init__(master)
		self.master = master
		self.community = community
		self.pack()
		self.createWidgets()
		self.updateWidgets()

	def createWidgets(self):
		self.exitBtn = Button(self, text="Close Library", command=self.closeWindow)
		self.exitBtn.pack(side=TOP)

		self.libraryListbox = Listbox(self, exportselection=False, height=20, width=60)
		self.libraryListbox.pack(side=TOP)

	def updateWidgets(self):
		self.libraryListbox.delete(0, END)
		for i in range(len(self.community.greatWorks)-1, -1, -1):
			w = self.community.greatWorks[i]
			self.libraryListbox.insert(END, "{}: {}, {}".format(w[1], w[0], self.dateToString(w[2])))

	def dateToString(self, d):
		# Discards season.
		year = BASE_YEAR + d//4
		return str(year)

	def closeWindow(self):
		self.master.grab_release()
		self.master.destroy()


if __name__ == "__main__":
	root = Tk()
	root.geometry("800x600")
	root.resizable(0, 0)
	app = Application(master=root)
	app.mainloop()
