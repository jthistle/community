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
		self.dateLabel = Label(self.btnFrame, text="")
		self.dateLabel.grid(row=0, column=4, sticky=E+W, padx=10)
		self.inspectBtn = Button(self.btnFrame, text="Inspect", command=self.onInspectBtnClick)
		self.inspectBtn.grid(row=0, column=5, sticky=E+W)
		self.compareBtn = Button(self.btnFrame, text="Compare", command=self.onCompareBtnClick)
		self.compareBtn.grid(row=0, column=6, sticky=E+W)
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

	def blank(self):
		'Placeholder function'
		None


class FamilyTree(Frame):
	def __init__(self, master=None, person=None):
		super().__init__(master)
		self.master = master
		self.person = person
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

	def updateWidgets(self):
		self.parentsLb.delete(0, END)
		if self.person.parents[0] is not None:
			for p in self.person.parents:
				toAppend = ""
				if not p.alive:
					toAppend = " (d.)"
				self.parentsLb.insert(END, p.printableFullName()+toAppend)

		self.siblingsLb.delete(0, END)
		toAppend = ""
		if not self.person.alive:
			toAppend = " (d.)"
		self.siblingsLb.insert(END, self.person.printableFullName()+toAppend)
		if self.person.married:
			toAppend = ""
			if not self.person.partner.alive:
				toAppend = " (d.)"
			self.siblingsLb.insert(END, "↳ (m) "+self.person.partner.printableFullName()+toAppend)

		if self.person.parents[0] is not None:
			siblings = self.person.parents[0].children
			for p in siblings:
				if p == self.person:
					continue
				toAppend = ""
				if not p.alive:
					toAppend = " (d.)"
				self.siblingsLb.insert(END, p.printableFullName()+toAppend)
		self.siblingsLb.selection_set(0)

		self.childrenLb.delete(0, END)
		for p in self.person.children:
			toAppend = ""
			if not p.alive:
				toAppend = " (d.)"
			self.childrenLb.insert(END, p.printableFullName()+toAppend)

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

	def closeWindow(self):
		self.master.grab_release()
		self.master.destroy()


if __name__ == "__main__":
	root = Tk()
	root.geometry("800x600")
	root.resizable(0, 0)
	app = Application(master=root)
	app.mainloop()
