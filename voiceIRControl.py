#! /usr/bin/env python
# -*- coding: utf-8 -*-

import asr
import time

import requests
import json

# GPIO settings
#import RPi.GPIO as GPIO

# logging libs
import logging
app_log = logging.getLogger('root')


# imports for CMU Sphinx voice activation
import sys, os
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

import alsaaudio
import wave

JSON_FILE_NAME = "device_config.json"
AUDIO_FILE_NAME = 'output.wav'
IR_IP_adress = '192.168.0.106:3000'
ZWAY_IP_adress = '192.168.0.106:8083'

KEYPHRASE = 'raspberry'
REC_TIME = 2

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

def speech2Text(stream, rate, chunk_size, rec_sec):
	text = []
	text = asr.yandexAsrMicStream(stream, rate, chunk_size, rec_sec)
	# convert to unicode
	text = text.decode('utf-8')
	text = text.lower()
	text.encode('utf-8')
	return text  

def recordAudio(audioFileName, rec_sec, stream):
	#recordAudioToFile.recAlsaAudio(audioFileName, rec_sec)
	#stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL)
	#stream.setchannels(CHANNELS)
	#stream.setrate(RATE)
	#stream.setformat(FORMAT_alsaaudio)
	#stream.setperiodsize(CHUNK)
	CHUNK = 1024
	RATE  = 16000
	FORMAT_PCM_FORMAT_S16_LE_size  = 2
	CHANNELS = 1
	frames = []

	for i in range(0, int(RATE / CHUNK * rec_sec)):
		l,data = stream.read()
		frames.append(data)

	wf = wave.open(audioFileName, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(FORMAT_PCM_FORMAT_S16_LE_size)
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close() 

def findMatch(text, commands):
	match = []
	for command in commands:
		if text.find(command, 0) != -1:
			match.append(command)
	return match

def commandToActionHttp(matchCommands, lib):
	for command in matchCommands:
		action = lib[command]
		ip_adress = []
		
		if action[0] == 'Z':
			ip_adress = ZWAY_IP_adress
			req_url = 'http://' + ip_adress + '/'  + action
			r = requests.get(req_url, auth=('admin', 'bzahome27')) # http request

		else:
			ip_adress = IR_IP_adress
			req_url = 'http://' + ip_adress + '/'  + action
			r = requests.get(req_url) # http request

		app_log.info('---- request url = ' + req_url)

    	return_mes = "returned: status_code = " + str(r.status_code)
    	return return_mes

# record audio *.wav file and send it to yandex 
def listenCommand(com_act_lib, rec_time, stream):
	#time.sleep(0.5)
	#  record speech audio file
	app_log.info('---- start to record audio')
	recordAudio(AUDIO_FILE_NAME, time, stream)
	app_log.info('---- stop to record audio')

	#  yandex speech recognition
	text = audio2Text(AUDIO_FILE_NAME)
	app_log.info('---- finished audio2Text')
	app_log.info('---- recognized text = ' + text)

	
	# find commands in text
	match = []
	if(text):
		match = findMatch(text, com_act_lib.keys())
		
	if (match):
		mes = commandToActionHttp(match, com_act_lib)
		app_log.info('---- device ' +  mes)
	else:
		app_log.info('---- no command matches')

# listen command directly from mic and send it to yandex 
def listenCommand2(com_act_lib, stream, rate, chunk_size, rec_sec):
	#yandex speech recognition
	app_log.info('---- start speech2Text')
	text = speech2Text(stream, rate, chunk_size, rec_sec)
	#app_log.info('---- text type ' + type(text))
	app_log.info('---- finished speech2Text')
	app_log.info('---- recognized text = ' + text)


	# find commands in text
	match = []
	if(text):
		match = findMatch(text, com_act_lib.keys())
		
	if (match):
		mes = commandToActionHttp(match, com_act_lib)
		app_log.info('---- device ' +  mes)
	else:
		app_log.info('---- no command matches')

def main():
	# setup GPIO. LED Indication
	#GPIO.setmode(GPIO.BCM)
	green = 12
	#GPIO.setup(green, GPIO.OUT) # green
	red = 16
	#GPIO.setup(red, GPIO.OUT) # red
	#GPIO.output(green, GPIO.HIGH)
	#GPIO.output(red, GPIO.HIGH)

	#change directory
	homedir = os.environ['HOME']
	currdir = os.getcwd()
	irdir = os.path.join(homedir, 'irControl/voice_command_recognition')
	#os.chdir(irdir)

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


	app_log.info('-- START voiceIRControl.py.')

	# read commands from json file
	com_act_lib = readJsonFile(JSON_FILE_NAME)
	app_log.info('-- finished to read device configuration json file ' + JSON_FILE_NAME)

	modeldir = "../pocketsphinx-python/pocketsphinx/model"
	datadir = "../pocketsphinx-python/pocketsphinx/test/data"
	# Create a decoder with certain model
	config = Decoder.default_config()
	config.set_string('-hmm', os.path.join(modeldir, 'en-us/en-us'))
	config.set_string('-dict', os.path.join(modeldir, 'en-us/cmudict-en-us.dict'))
	config.set_string('-keyphrase', KEYPHRASE)
	config.set_float('-kws_threshold', 1e-40)
	app_log.info('-- finished to set CMU SPHINX library settings')


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
	app_log.info('-- finished to set alsaaudio parameters')

	# Process audio chunk by chunk. 
	decoder = Decoder(config)
	decoder.start_utt()
	

	while True:
		#GPIO.output(green, GPIO.HIGH)
		#GPIO.output(red, GPIO.LOW)

		l, buf = stream.read()
		if buf:
		    decoder.process_raw(buf, False, False)
		else:
			app_log.info('-- no data from stream')
		    #break
		if decoder.hyp() != None:
			
			#GPIO.output(green, GPIO.LOW)
			#GPIO.output(red, GPIO.HIGH)

			app_log.info('-- detected keyphrase ' + KEYPHRASE)
			decoder.end_utt()

			try:
				app_log.info('-- start listenCommand')
				#listenCommand(com_act_lib, REC_TIME, stream)
				listenCommand2(com_act_lib, stream, RATE, CHUNK, REC_TIME)
				app_log.info('-- stop listenCommand')
			except Exception:
				app_log.info("-- Unexpected error:" + str(sys.exc_info()))

			decoder.start_utt()

if __name__ == "__main__":
        main()



