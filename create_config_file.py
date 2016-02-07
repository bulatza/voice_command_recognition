#! /usr/bin/env python
# -*- coding: utf-8 -*-

# JSON device configuration file encoder and decoder.
import json 

jsonFileName = "new_deviceConfig.json"

device = "LG_AKB72915207"

button = [
'KEY_POWER',
'KEY_POWER', 
'KEY_1',
'KEY_2',
'KEY_3',
'KEY_4',
'KEY_5',
'KEY_6',
'KEY_7',
'KEY_8',
'KEY_9',
'KEY_0',
'KEY_VOLUMEUP',
'KEY_VOLUMEDOWN',
'KEY_CHANNELUP',
'KEY_CHANNELDOWN',
'KEY_MENU',
'KEY_UP',
'KEY_DOWN',
'KEY_RIGHT',
'KEY_LEFT',
'KEY_OK'
]

voice_command = [
'включить',
'выключить',
'1',
'2',
'3',
'4',
'5',
'6',
'7',
'8',
'9',
'0',
'громкость +',
'громкость -',
'canal +',
'канал -',
'меню',
'вверх',
'вниз',
'вправо',
'влево',
'ок'
]

def write2Json(file_name, device, buttons, voice_commands):
	f = open(file_name, "w")
	dev_buttons = []
	for i in range(0, len(buttons)):
		action1 = '/send/' + device + '/' + buttons[i]
		dev_buttons.append({'device_name': device, 
							'button' :buttons[i], 
							'actions': [action1], 
							'voice_command': voice_commands[i]})

	dict_device = dev_buttons 
	json.dump(dict_device, f, ensure_ascii = False, sort_keys=True,  indent=4, separators=(',', ': '))
	f.close()

def readJsonFile(file_name):
	f = open(file_name, "r")
	jdata = json.load(f)
	f.close()
	# parse jdata
	commands = []
	actions = []
	for button in jdata:
		commands.append(button['voice_command'])
		actions.append(button['actions'])
	return dict(zip(commands, actions)) 

def main():
	# write data to json file
	write2Json(jsonFileName, device, button, voice_command)
	print "data was written"

	# read data from json file
	data = readJsonFile(jsonFileName)
	print 'data in file: '
	print data


if __name__ == '__main__':
    main()
