# -*- coding: utf-8 -*-
# JSON device configuration file encoder and decoder.
import json 

jsonFileName = "device_config.json"

device = 'TV-LG'

name = [
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
'громкость прибавить',
'громкость убавить',
'канал следующий',
'канал предыдущий',
'меню',
'вверх',
'вниз',
'вправо',
'влево',
'ок'
]

action = [
'http://192.168.0.104/send/LG/KEY_POWER',
'http://192.168.0.104/send/LG/KEY_POWER',
'http://192.168.0.104/send/LG/KEY_1', 
'http://192.168.0.104/send/LG/KEY_2',
'http://192.168.0.104/send/LG/KEY_3', 
'http://192.168.0.104/send/LG/KEY_4',
'http://192.168.0.104/send/LG/KEY_5', 
'http://192.168.0.104/send/LG/KEY_6',
'http://192.168.0.104/send/LG/KEY_7', 
'http://192.168.0.104/send/LG/KEY_8',
'http://192.168.0.104/send/LG/KEY_9', 
'http://192.168.0.104/send/LG/KEY_0',
'http://192.168.0.104/send/LG/KEY_VOLUMEUP', 
'http://192.168.0.104/send/LG/KEY_VOLUMEDOWN',
'http://192.168.0.104/send/LG/KEY_CHANNELUP', 
'http://192.168.0.104/send/LG/KEY_CHANNELDOWN',
'http://192.168.0.104/send/LG/KEY_MENU', 
'http://192.168.0.104/send/LG/KEY_UP',
'http://192.168.0.104/send/LG/KEY_DOWN', 
'http://192.168.0.104/send/LG/KEY_RIGHT',
'http://192.168.0.104/send/LG/KEY_LEFT', 
'http://192.168.0.104/send/LG/KEY_OK'
]


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
	device = jdata['TV-LG']
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