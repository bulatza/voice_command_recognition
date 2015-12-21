# -*- coding: utf-8 -*-
import requests
import asr
import recordAudioToFile
import time
import json


JSON_FILE_NAME = 'device_config.json'
AUDIO_FILE_NAME = 'output.wav'


def readCommandFile(file_name):
	f = open(file_name, 'r')
 	text = f.readlines()
 	commands = []
 	for command in text:
 		commands.append(command[0:-1])

 	f.close()
 	return commands

def readActionFile(file_name):
	f = open(file_name, 'r')
	actions = []
 	text2 = f.readlines()
   	for action in text2:
   		actions.append(action[0:-1])
 	f.close()
 	return actions

def commandToActionLib(commands, actions):
	comActLib = dict(zip(commands, actions))
	return comActLib

def readJsonFile(file_name):
	f = open(file_name, "r")
	jdata = json.load(f)
	f.close()
	# parse jdata for 'TV'
	device = jdata['TV']
	commands = []
	actions = []
	for button in device:
		commands.append(button['voice_command'])
		actions.append(button['action'])
	return dict(zip(commands, actions)) 

def audio2Text(audioFileName):
	text = asr.yandexAsrFile(audioFileName)
	# convert to unicode
	text = text.decode('utf-8')
	return text

def speech2Text():
	text = []
	text = asr.yandexAsrMic()
	# convert to unicode
	text = text.decode('utf-8')
	return text  

def recordAudio(audioFileName, recTime):
	recordAudioToFile.recAudio(audioFileName, recTime) 

def findMatch(text, commands):
	match = []
	for command in commands:
		if text.find(command, 0) != -1:
			match.append(command)
	return match

def commandToActionHttp(matchCommands, lib):
	for command in matchCommands:
		req_url = lib[command]
		print "---- apply action: " + req_url + " for command: " + command 
    	r = requests.get(req_url) # http request
    	print "---- IR server returned: status_code = " + str(r.status_code) + ", content = " + r.content
    	return r.status_code


def main():
	# read commands from json file
	com_act_lib = readJsonFile(JSON_FILE_NAME)

	while True:
		time.sleep(0.5)
		#  record speech audio file
		print "--- START to RECORD AUDIO"
		recordAudio(AUDIO_FILE_NAME, 2)
		print "--- STOP to RECORD AUDIO"

		#  yandex speech recognition
		text = audio2Text(AUDIO_FILE_NAME)
		#text = unicode(text,'utf-8').lower();
		print "--- audio2Text recognized text = " + text
        
		# find commands in text
		match = []
		if(text):
			match = findMatch(text, com_act_lib.keys())
			print "--- matches have been founded = "
			for command in match:
				print command
		else:
			print "--- no text"

		if (match):
			commandToActionHttp(match, com_act_lib)
			print "--- apply action"
		else:
			print "--- no matches"

if __name__ == "__main__":
        main()



