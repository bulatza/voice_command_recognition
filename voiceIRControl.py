#! /usr/bin/env python
# -*- coding: utf-8 -*-

# yandex SpeechKit
import asr
import time

import requests
import json

# GPIO settings
from gpio_led import Gpioled
gl = Gpioled(12, 16, 0.2) # green, red, dt

# logging libs
import logging
app_log = logging.getLogger('root')

# imports for CMU Sphinx voice activation
import sys, os
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

# audio streaming
import alsaaudio
import wave

# get raspberry ip adress
import pi_adress

JSON_FILE_NAME = 'device_config.json'
LOG_FILE = 'voiceIRControl.log'

AUDIO_FILE_NAME = 'output.wav'
IR_IP_adress = '0.0.0.0:3000'
ZWAY_IP_adress = '0.0.0.0:8083'

# settings for key phrase detecting
KEYPHRASE = 'raspberry'
KEYPHRASE_ERR = 1e-30
REC_TIME = 2

def set_ip_adress():
	global IR_IP_adress
	IR_IP_adress = pi_adress.primary_ip_adress() + ':3000'
	global ZWAY_IP_adress
	ZWAY_IP_adress = pi_adress.primary_ip_adress() + ':8083'

def readJsonCommandFile(file_name):
	f = open(file_name, "r")
	jdata = json.load(f)
	f.close()
	# parse jdata
	commands = []
	actions = []
	for button in jdata:
		commands.append(button['voice_command'])
		actions.append(button['action'])
	#app_log.info('---- jdata =' + str())
	return dict(zip(commands, actions)) 

def readDeviceCommand(ip_adress):
	req_url = 'http://' + ip_adress + '/commands/json'
	r = requests.get(req_url)
	app_log.info('---- request commands url = ' + req_url)
	# get all json format data
	jdata = r.json()
	# parse data
	commands = []
	actions = []
	i = 1
	for button in jdata:
		command = button['voice_command']
		action = button['action']
		commands.append(command)
		actions.append(action)
		app_log.info('---- command[' + str(i) + '] - ' + command + '  =>  action[' + str(i) + '] - ' + action)
		i = i + 1

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
		
		if action[1] == 'Z':
			ip_adress = ZWAY_IP_adress
			req_url = 'http://' + ip_adress + action
			r = requests.get(req_url, auth=('admin', 'bzahome27')) # http request

		else:
			ip_adress = IR_IP_adress
			req_url = 'http://' + ip_adress + action
			r = requests.get(req_url) # http request

		app_log.info('---- request url = ' + req_url)
		if r.status_code == 200:
			gl.goodStatus()
		else:
			gl.badStatus()    	
	return r.status_code

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
			status_code = commandToActionHttp(match, com_act_lib)
			app_log.info('---- device returned status: ' +  str(status_code))
		else:
			gl.badStatus()
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
			status_code = commandToActionHttp(match, com_act_lib)
			app_log.info('---- device returned status:' +  str(status_code))
		else:
			gl.badStatus()
			app_log.info('---- no command matches')

def main(): 		
	
	gl.high()

	# change directory
	homedir = os.environ['HOME']
	currdir = os.getcwd()
	irdir = os.path.join(homedir, 'irControl/voice_command_recognition')
	#os.chdir(irdir)

	# set logging info
	log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	log_file = LOG_FILE
	from logging.handlers import RotatingFileHandler
	file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
	file_handler.setFormatter(log_formatter)
	file_handler.setLevel(logging.INFO)
	app_log.setLevel(logging.INFO)
	app_log.addHandler(file_handler)

        app_log.info('-- START voiceIRControl.py. from directory ' + currdir)
	
        # set IP adresses
        set_ip_adress()
        app_log.info('-- IR_IP_adress ' + IR_IP_adress)
        app_log.info('-- ZWAY_IP_adress ' + ZWAY_IP_adress)
	
	# read commands from json file
	com_act_lib = readJsonCommandFile(JSON_FILE_NAME)
	#com_act_lib = readDeviceCommand(IR_IP_adress)
	app_log.info('-- finished to read device configuration json file ' + JSON_FILE_NAME)

	modeldir = "../pocketsphinx-python/pocketsphinx/model"
	datadir = "../pocketsphinx-python/pocketsphinx/test/data"
	# Create a decoder with certain model
	config = Decoder.default_config()
	config.set_string('-hmm', os.path.join(modeldir, 'en-us/en-us'))
	config.set_string('-dict', os.path.join(modeldir, 'en-us/cmudict-en-us.dict'))
	config.set_string('-keyphrase', KEYPHRASE) 
	config.set_float('-kws_threshold', KEYPHRASE_ERR)
	app_log.info('-- finished to set CMU SPHINX library settings')

	# alsaaudio settings
	CHUNK = 1024
	FORMAT = alsaaudio.PCM_FORMAT_S16_LE
	CHANNELS = 1
	RATE = 16000
	try:	
		stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL)
		stream.setchannels(CHANNELS)
		stream.setrate(RATE)
		stream.setformat(FORMAT)
		stream.setperiodsize(CHUNK)
		app_log.info('-- finished to set alsaaudio parameters')
	except Exception:
		app_log.info('-- alsaaudio unexpected error:' + str(sys.exc_info()))
		
		gl.errorStatus()
		app_log.info('-- exit from programm sys.exit(1)')
		sys.exit(1)

	# Process audio chunk by chunk. 
	decoder = Decoder(config)
	decoder.start_utt()
	
	while True:
		gl.wait()

		l, buf = stream.read()
		if buf:
		    	decoder.process_raw(buf, False, False)
		else:
			app_log.info('-- no data from stream')

		if decoder.hyp() != None:
			
			gl.rec()
			app_log.info('-- detected keyphrase ' + KEYPHRASE)
			decoder.end_utt()

			try:
				app_log.info('-- start listenCommand')
				listenCommand2(com_act_lib, stream, RATE, CHUNK, REC_TIME)
				app_log.info('-- stop listenCommand')
			except Exception:
				app_log.info("-- unexpected error:" + str(sys.exc_info()))
				gl.errorStatus()
			
			decoder.start_utt()

if __name__ == "__main__":
        main()



