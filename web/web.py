#!/usr/bin/env python3

import sys
import pickle
import json
import os.path

'''
Arguments:

getState
getName
'''

try:
	from community import Community
except Exception as e:
	print(e)

SAVE_LOCATION = "savefiles/"


def loadCommunity(userId):
	try:
		if os.path.isfile(SAVE_LOCATION+userId+".cmu"):
			with open(SAVE_LOCATION+userId+".cmu", "rb") as file:
				tempCom = pickle.load(file)
				if isinstance(tempCom, Community):
					return tempCom
				else:
					raise Exception("Could not decode community from save file")
		return False
	except Exception as e:
		returnMessage(e)


def saveCommunity(userId, c):
	with open(SAVE_LOCATION+userId+".cmu", "wb") as file:
		pickle.dump(c, file)
		return True
	return False


def returnMessage(s):
	print(json.dumps({"reponseType": "information", "text": s}))


try:
	if len(sys.argv) > 2:
		userId = sys.argv[1]
		arg = sys.argv[2]
		current = None

		if arg == "getState":
			current = loadCommunity(userId)
			if current:
				returnMessage("ready")
			else:
				returnMessage("not initialised")

		elif arg == "init":
			if os.path.isfile(SAVE_LOCATION+userId+".cmu"):
				returnMessage("already exists")
			else:
				with open(SAVE_LOCATION+userId+".cmu", "wb") as file:
					c = Community()
					pickle.dump(c, file)
					returnMessage("done")

		elif arg == "clear":
			if os.path.isfile(SAVE_LOCATION+userId+".cmu"):
				os.remove(SAVE_LOCATION+userId+".cmu")
				returnMessage("done")
			else:
				returnMessage("no file to remove")

		elif arg == "getCommunityLog":
			current = loadCommunity(userId)
			if current:
				print(json.dumps(current.eventLog))
			else:
				returnMessage("error: not initialised")

		elif arg == "testGetName":
			current = loadCommunity(userId)
			if current:
				name = current.families[0].people[0].printableFullName()
				print(json.dumps({"responseType": "value", "name": name}))
			else:
				returnMessage("error: not initialised")
		else:
			returnMessage("unrecognised command "+arg)

		if current:
			saveCommunity(userId, current)
	else:
		returnMessage("error: not enough argumuents")

except Exception as e:
	returnMessage(e)
