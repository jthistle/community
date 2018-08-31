#!/usr/bin/env python3

from tkinter import *
import random
import math
import sys
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
		self.saveBtn = Button(self.btnFrame, text="Save", command=self.blank)
		self.saveBtn.grid(row=0, column=1, sticky=E+W)
		self.loadBtn = Button(self.btnFrame, text="Load", command=self.blank)
		self.loadBtn.grid(row=0, column=2, sticky=E+W)
		self.exitBtn = Button(self.btnFrame, text="Exit", command=root.destroy)
		self.exitBtn.grid(row=0, column=3, sticky=E+W)
		self.dateLabel = Label(self.btnFrame, text="")
		self.dateLabel.grid(row=0, column=4, sticky=E+W, padx=10)
		self.inspectBtn = Button(self.btnFrame, text="Inspect", command=self.blank)
		self.inspectBtn.grid(row=0, column=5, sticky=E+W)
		self.inspectBtn.bind('<Button-1>', self.onInspectBtnClick)
		self.compareBtn = Button(self.btnFrame, text="Compare", command=self.blank)
		self.compareBtn.grid(row=0, column=6, sticky=E+W)
		self.compareBtn.bind('<Button-1>', self.onCompareBtnClick)

		self.restFrame = Frame()
		self.restFrame.pack(fill=X)
		self.restFrame.grid_columnconfigure(0, minsize=5, weight=0)
		self.restFrame.grid_columnconfigure(1, minsize=5, weight=0)
		self.restFrame.grid_columnconfigure(2, minsize=5, weight=1)

		self.familiesLabel = Label(self.restFrame, text="Families")
		self.familiesLabel.grid(row=0, column=0, sticky=W)
		self.familiesList = Listbox(self.restFrame)
		self.familiesList.grid(row=1, column=0, sticky=E+W, padx=5)
		self.familiesList.bind('<<ListboxSelect>>', self.onFamiliesLbChange)

		self.peopleLabel = Label(self.restFrame, text="People")
		self.peopleLabel.grid(row=0, column=1, sticky=W)
		self.peopleList = Listbox(self.restFrame)
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

		self.eventsLabel = Label(self.restFrame, text="Events")
		self.eventsLabel.grid(row=2, column=0, sticky=W)
		self.eventLog = Text(self.restFrame, width=50, height=19, state=DISABLED)
		self.eventLog.grid(row=3, column=0, columnspan=2, sticky=N+E+W+S, padx=5)

	def updateWidgets(self):
		self.dateLabel.config(text=self.community.dateToString())
		self.familiesList.delete(0, END)
		for f in self.community.families:
			self.familiesList.insert(END, f.familyName)
		self.updatePeopleList()
		self.updateMainEventLog()

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
			f = self.community.getFamilyByIndex(self.selectedFamily)
			for p in f.people:
				self.peopleList.insert(END, p.firstName())

	def inspectFamily(self):
		self.lastInspected = "family"
		f = self.community.getFamilyByIndex(self.selectedFamily)
		self.writeToInspector(f.inspect())
		self.writeInspectorEvents(f.eventLog)

	def inspectPerson(self):
		self.lastInspected = "person"
		if self.selectedPerson is not None:
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

	def onInspectBtnClick(self, evt):
		self.viewMode = "inspect"
		self.comparePerson = None
		self.updateWidgets()

	def onCompareBtnClick(self, evt):
		if self.selectedPerson is not None and self.lastInspected == "person":
			self.viewMode = "compare"
			self.comparePerson = self.getSelectedPerson()
			self.writeToInspector("Select a person to compare to {}".format(self.comparePerson.firstName()))
			self.writeInspectorEvents([])  # clear events panel
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
		f = self.community.getFamilyByIndex(self.selectedFamily)
		p = f.getPerson(self.selectedPerson)
		return p

	def passTime(self):
		self.community.passTime()
		self.updateWidgets()

	def blank(self):
		'Placeholder function'
		None


if __name__ == "__main__":
	root = Tk()
	root.geometry("800x600")
	root.resizable(0, 0)
	app = Application(master=root)
	app.mainloop()
