def findMatch(text, commands):
        match_commands = {}
        for command in commands:
                beg = 0
                match_pos = text.find(command, beg)
		while match_pos != -1:
                        match_commands[str(match_pos)] = command
                        print('------ command ' + command + ' matched in posotion ' + str(match_pos + 1))
			beg = match_pos + 1
                        match_pos = text.find(command, beg)

        # sort finded commands
	print match_commands
        import operator
        match_sort = sorted(match_commands.items(), key = operator.itemgetter(0))
       	print match_sort
	match = []
	if match_sort:
       		print('---- sorted matched commands :' )
                for command in match_sort:
                        print('------ ' + command[1] )
			match.append(command[1])
        else:
                print('---- no command matches')

        return match

