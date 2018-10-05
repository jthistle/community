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
	print(json.dumps({"responseType": "information", "value": str(s)}))


def returnError(s):
	print(json.dumps({"responseType": "error", "value": "error: "+str(s)}))


try:
	if len(sys.argv) > 2:
		userId = sys.argv[1]
		arg = sys.argv[2]
		otherArgs = sys.argv[3:]
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

		elif arg == "passTime":
			current = loadCommunity(userId)
			if current:
				current.passTime()
				returnMessage("done")
			else:
				returnError("not initialised")

		elif arg == "getCommunityLog":
			current = loadCommunity(userId)
			if current:
				if otherArgs[0] == "latest":
					tempLog = []
					for i in range(len(current.eventLog)-1, -1, -1):
						tempLog.append(current.eventLog[i])
						if current.eventLog[i][0] == "=":
							break

					print(json.dumps({"responseType": "array", "value": list(reversed(tempLog))}))
			else:
				returnError("not initialised")

		elif arg == "getPersonLog":
			current = loadCommunity(userId)
			if current:
				familyInd = int(otherArgs[0])
				personInd = int(otherArgs[1])
				if otherArgs[2] == "latest":
					# TODO: debug replace
					eventLog = current.families[familyInd].people[personInd].eventLog
					tempLog = []
					for i in range(len(eventLog)-1, -1, -1):
						tempLog.append(eventLog[i])
						if eventLog[i][0] == "=":
							break
					print(json.dumps({"responseType": "array", "value": list(reversed(tempLog))}))
			else:
				returnError("not initialised")

		elif arg == "getFamilies":
			current = loadCommunity(userId)
			if current:
				toReturn = [f.familyName for f in current.families]
				print(json.dumps({"responseType": "array", "value": list(toReturn)}))
			else:
				returnError("not initialised")

		elif arg == "getPeople":
			current = loadCommunity(userId)
			if current:
				ind = int(otherArgs[0])
				toReturn = [p.firstName() for p in current.families[ind].people]
				print(json.dumps({"responseType": "array", "value": list(toReturn)}))
			else:
				returnError("not initialised")

		elif arg == "inspectPerson":
			current = loadCommunity(userId)
			if current:
				familyInd = int(otherArgs[0])
				personInd = int(otherArgs[1])
				toReturn = current.families[familyInd].people[personInd].inspectWeb()
				print(json.dumps({"responseType": "array", "value": toReturn}))
			else:
				returnError("not initialised")

		else:
			returnError("unrecognised command "+arg)

		if current:
			saveCommunity(userId, current)
	else:
		returnError("not enough argumuents")
except Exception as e:
	returnError(e)
