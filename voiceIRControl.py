# -*- coding: utf-8 -*-
import requests
import asr
import recordAudioToFile
import time
import json

import logging
app_log = logging.getLogger('root')


# imports for CMU Sphinx voice activation
import sys, os
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
import alsaaudio

sys.stdout.flush()

JSON_FILE_NAME = 'device_config.json'
AUDIO_FILE_NAME = 'output.wav'
IP_adress = '192.168.0.106:3000'
KEYPHRASE = 'raspberry'

def readJsonFile(file_name):
	f = open(file_name, "r")
	jdata = json.load(f)
	f.close()
	# parse jdata
	commands = []
	actions = []
	for button in jdata:
		commands.append(button['voice_command'])
		actions.append(button['action'])
	
	return dict(zip(commands, actions)) 

def audio2Text(audioFileName):
	text = asr.yandexAsrFile(audioFileName)
	# convert to unicode
	text = text.decode('utf-8')
	text = text.lower()
	text.encode('utf-8')
	return text

def speech2Text():
	text = []
	text = asr.yandexAsrMic()
	# convert to unicode
	text = text.decode('utf-8')
	text = text.lower()
	text.encode('utf-8')
	return text  

def recordAudio(audioFileName, recTime):
	recordAudioToFile.recAlsaAudio(audioFileName, recTime) 

def findMatch(text, commands):
	match = []
	for command in commands:
		if text.find(command, 0) != -1:
			match.append(command)
	return match

def commandToActionHttp(matchCommands, lib):
	for command in matchCommands:
		req_url = 'http://' + IP_adress + '/'  + lib[command]
		app_log.info('-----request url = ' + req_url)
    	r = requests.get(req_url) # http request
    	#print "---- IR server returned: status_code = " + str(r.status_code) + ", content = " + r.content
    	return r.status_code

def listenCommand(com_act_lib, time):
	#time.sleep(0.5)
	#  record speech audio file
	app_log.info('-----start to record audio')
	recordAudio(AUDIO_FILE_NAME, time)
	app_log.info('-----stop to record audio')

	#  yandex speech recognition
	text = audio2Text(AUDIO_FILE_NAME)
	app_log.info('-----finished audio2Text')
	
	# find commands in text
	match = []
	if(text):
		match = findMatch(text, com_act_lib.keys())
		
	if (match):
		status = commandToActionHttp(match, com_act_lib)
		if status == 200:
			app_log.info('-----success - ' + str(status))
		else:
			app_log.info('-----not success - ' + str(status))
	else:
		app_log.info('-----not command matches')

def main():
	# set logging info
	log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	log_file = 'voiceIRControl.log'

	from logging.handlers import RotatingFileHandler
	file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
	file_handler.setFormatter(log_formatter)
	file_handler.setLevel(logging.INFO)


	app_log.setLevel(logging.INFO)
	app_log.addHandler(file_handler)


	app_log.info('----START voiceIRControl.py.')

	# read commands from json file
	com_act_lib = readJsonFile(JSON_FILE_NAME)
	app_log.info('----finished to read device configuration json file ' + JSON_FILE_NAME)

	modeldir = "../../pocketsphinx-python/pocketsphinx/model"
	datadir = "../../pocketsphinx-python/pocketsphinx/test/data"
	# Create a decoder with certain model
	config = Decoder.default_config()
	config.set_string('-hmm', os.path.join(modeldir, 'en-us/en-us'))
	config.set_string('-dict', os.path.join(modeldir, 'en-us/cmudict-en-us.dict'))
	config.set_string('-keyphrase', KEYPHRASE)
	config.set_float('-kws_threshold', 1e-40)
	app_log.info('----finished to set CMU SPHINX library settings')


	# alsaaudio settings
	CHUNK = 1024
	FORMAT = alsaaudio.PCM_FORMAT_S16_LE
	CHANNELS = 1
	RATE = 16000
	stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL)
	stream.setchannels(CHANNELS)
	stream.setrate(RATE)
	stream.setformat(FORMAT)
	stream.setperiodsize(CHUNK)
	app_log.info('----finished to set alsaaudio parameters')

	# Process audio chunk by chunk. 
	decoder = Decoder(config)
	decoder.start_utt()
	while True:
	    l, buf = stream.read()
	    if buf:
	         decoder.process_raw(buf, False, False)
	    else:
	    	app_log.info('----no data from stream')
	        break
	    if decoder.hyp() != None:
	    	app_log.info('----detected keyphrase ' + KEYPHRASE)
	        decoder.end_utt()
	        
	        try:
	       		app_log.info('----start listenCommand')
	       		listenCommand(com_act_lib, 3)
	       		app_log.info('----stop listenCommand')
	        except Exception, details:
	       		app_log.info("Unexpected error:" + str(sys.exc_info()))
	        
	        decoder.start_utt()

if __name__ == "__main__":
        main()



