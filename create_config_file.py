# -*- coding: utf-8 -*-
# JSON device configuration file encoder and decoder.
import json 

jsonFileName = "device_config.json"

device = 'TV'

name = [
'KEY_POWER', 
'KEY_UP',
'KEY_DOWN']

voice_command = [
'включить',
'синий',
'зеленый']

action = [
'http://192.168.0.104/send/RGBW/KEY_POWER', 
'http://192.168.0.104/send/RGBW/KEY_UP',
'http://192.168.0.104/send/RGBW/KEY_DOWN']


def write2Json(file_name, device, names, voice_commands, actions):
	f = open(file_name, "w")
	dev_buttons = []
	for i in range(0, len(names)):
		dev_buttons.append({'name' :names[i], 'action': actions[i], 'voice_command': voice_commands[i]})

	dict_device = {device: dev_buttons} 
	json.dump(dict_device, f, ensure_ascii = False, sort_keys=True,  indent=4, separators=(',', ': '))
	f.close()

def read4Json(file_name):
	f = open(file_name, "r")
	jdata = json.load(f)
	f.close()
	# parse jdata
	device = jdata['TV']
	commands = []
	actions = []
	for button in device:
		commands.append(button['voice_command'])
		actions.append(button['action'])
	return dict(zip(commands, actions)) 

def main():
	# write data to json file
	write2Json(jsonFileName, device, name, voice_command, action)
	print "data was written"

	# read data from json file
	data = read4Json(jsonFileName)
	print 'data in file: '
	print data


if __name__ == '__main__':
    main()