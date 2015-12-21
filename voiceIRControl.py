# -*- coding: utf-8 -*-
import requests
import asr
import recordAudioToFile
import time
import json

# imports for CMU Sphinx voice activation
import sys, os
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
import pyaudio

JSON_FILE_NAME = 'device_config.json'
AUDIO_FILE_NAME = 'output.wav'

def readJsonFile(file_name):
	f = open(file_name, "r")
	jdata = json.load(f)
	f.close()
	# parse jdata for 'TV-LG'
	device = jdata['TV-LG']
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
	text = text.lower()
	return text

def speech2Text():
	text = []
	text = asr.yandexAsrMic()
	# convert to unicode
	text = text.decode('utf-8')
	text = text.lower()
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

def listenCommand(com_act_lib):
	#time.sleep(0.5)
	#  record speech audio file
	print "--- START to RECORD AUDIO"
	recordAudio(AUDIO_FILE_NAME, 3)
	print "--- STOP to RECORD AUDIO"

	#  yandex speech recognition
	text = audio2Text(AUDIO_FILE_NAME)
	#text = unicode(text,'utf-8').lower();
	print "--- audio2Text recognized text = " + text
    
	# find commands in text
	match = []
	if(text):
		match = findMatch(text, com_act_lib.keys())
		
	if (match):
		commandToActionHttp(match, com_act_lib)
		print "--- apply action"
	else:
		print "--- no matches"

def main():
	# read commands from json file
	com_act_lib = readJsonFile(JSON_FILE_NAME)

	modeldir = "/home/bulat/pocketsphinx-python/pocketsphinx/model"
	datadir = "/home/bulat/pocketsphinx-python/pocketsphinx/test/data"
	# Create a decoder with certain model
	config = Decoder.default_config()
	config.set_string('-hmm', os.path.join(modeldir, 'en-us/en-us'))
	config.set_string('-dict', os.path.join(modeldir, 'en-us/cmudict-en-us.dict'))
	config.set_string('-keyphrase', 'raspberry')
	config.set_float('-kws_threshold', 1e-20)

	p = pyaudio.PyAudio()
	stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
	stream.start_stream()
	# Process audio chunk by chunk. 
	decoder = Decoder(config)
	decoder.start_utt()
	while True:
	    buf = stream.read(1024)
	    if buf:
	         decoder.process_raw(buf, False, False)
	    else:
	         break
	    if decoder.hyp() != None:
	        #print ([(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in decoder.seg()])
	        print ("Detected keyword, restarting search")
	        decoder.end_utt()
	        listenCommand(com_act_lib)
	        decoder.start_utt()

if __name__ == "__main__":
        main()



