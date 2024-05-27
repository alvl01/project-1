#-*- coding: utf-8 -*-

import blessed, math, os, time, ai, ai2
term = blessed.Terminal()

# clear screen and hide cursor
print(term.home + term.clear + term.hide_cursor)

from remote_play import create_connection, get_remote_orders, notify_remote_orders, close_connection


#########################################################################
####                               MAIN                              ####
#########################################################################

def play_game(map_path, group_1, type_1, IP1, group_2, type_2, IP2):
	"""Play a game.

	Parameters
	----------
	map_path: path of map file (str)
	group_1: group of player 1 (int)
	type_1: type of player 1 (str)
	group_2: group of player 2 (int)
	type_2: type of player 2 (str)

	Notes
	-----
	Player type is either 'human', 'AI' or 'remote'.

	If there is an external referee, set group id to 0 for remote player.

	"""
	#create the data of the board
	data = getData(map_path)
	data = appearSheep(data, 1)
	data = appearSheep(data, 2)
	orders = {
		'player1':"",
		'player2':"",
		'player1_formated':[],
		'player2_formated':[]
	}
	grass_expension = {
		'number_grass_player_1': 0,
		'number_grass_player_2': 0,
		'time_without_expend_player_1': 0,
		'time_without_expend_player_2': 0
	}
	print_grid(term, data)

	...
	...

	# create connection, if necessary
	if type_1 == 'remote':
		connection = create_connection(group_2, group_1, IP1)
	elif type_2 == 'remote':
		connection = create_connection(group_1, group_2, IP2)
	...
	...
	...
	printData(term, data)
	boocs = False
	while not did_game_ended(data, grass_expension):
		if type_1 == 'remote':
			orders['player1'] = get_remote_orders(connection)
		if type_1 == 'AI':
			orders['player1'] = ai.get_AI_orders(data, 1)
			if type_2 == 'remote':
				notify_remote_orders(connection, orders['player1'])
		elif type_1 == 'human':
			orders['player1'] = input()
			position = [data['map_size'][0] + 1, 1]
			print_char_at('cmd> ' + ' ' * len(orders['player1']), position, term, data)
			if type_2 == 'remote':
				notify_remote_orders(connection, orders['player1'])
		if type_2 == 'remote':
			orders['player2'] = get_remote_orders(connection)
		if type_2 == 'AI':
			orders['player2'] = ai.get_AI_orders(data, 2)
			if type_1 == 'remote':
				notify_remote_orders(connection, orders['player2'])
		elif type_2 == 'human':
			orders['player2'] = input()
			position = [data['map_size'][0] + 1, 1]
			print_char_at('cmd> ' + ' ' * len(orders['player2']), position, term, data)
			if type_2 == 'remote':
				notify_remote_orders(connection, orders['player2'])

		orders['player1_formated'] = [order_format_verif(order) for order in orders['player1'].split(' ')]
		orders['player2_formated'] = [order_format_verif(order) for order in orders['player2'].split(' ')]
		data = execute_orders_step_by_step(data, orders)
		data = growGrass(data, 1)
		data = growGrass(data, 2)
		printData(term, data)
		if len(data['grass_player1']) > grass_expension['number_grass_player_1']:
			grass_expension['number_grass_player_1'] = len(data['grass_player1'])
			grass_expension['time_without_expend_player_1'] = 0
		else:
			grass_expension['time_without_expend_player_1'] += 1
		if len(data['grass_player2']) > grass_expension['number_grass_player_2']:
			grass_expension['number_grass_player_2'] = len(data['grass_player2'])
			grass_expension['time_without_expend_player_2'] = 0
		else:
			grass_expension['time_without_expend_player_2'] += 1
		#print(str(orders))

		time.sleep(0.1)

	printData(term, data, winner=get_winner(data, grass_expension))

	# close connection, if necessary
	if type_1 == 'remote' or type_2 == 'remote':
		close_connection(connection)

def did_game_ended(data, grass_expension):
	"""this function will verify if the game ended or not
	
	parameters
	----------
	data (dict) : A dictionary containing information about the game board.
        It should have the following keys:
		    -'sheep_player1': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            -'sheep_player2': A list of dictionaries representing a player's sheep with these hit point of life and its position
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.

	grass_expension (int) : the time that the grass did not expand  
	         
	return (bool) : false if the game still goign on 
	                true if the game ended 
                 
            

     Version
     -------
    specification: Al bayati Ahmed (v.2 15/03/24)
	"""
	if len(data['grass_player1']) >= 100 or len(data['grass_player2']) >= 100:
		return True
	if grass_expension['time_without_expend_player_2'] >= 20 or grass_expension['time_without_expend_player_1'] >= 20:
		return True
	return False

def get_winner(data, grass_expension):
	"""this function will get you the winner of a game played
	
	parameters
	----------
	data (dict) :  A dictionary containing information about the game board.
        It should have the following keys:
		    -'sheep_player1': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            -'sheep_player2': A list of dictionaries representing a player's sheep with these hit point of life and its position
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
 
     grass_expension (int) : the time that the grass did not expand 

	 return (int) : winner 
    
	 Version
     -------
     specification: Awan Muhammad Ammar (v.2 21/03/24)
	 
	"""
	if grass_expension['time_without_expend_player_1'] >= 20 and grass_expension['time_without_expend_player_2'] >= 20:
		return 3
	if grass_expension['time_without_expend_player_1'] >= 20:
		return 2
	if grass_expension['time_without_expend_player_2'] >= 20:
		return 1
	if len(data['grass_player1']) >= 100 and len(data['grass_player2']) < 100:
		return 1
	if len(data['grass_player1']) < 100 and len(data['grass_player2']) >= 100:
		return 2
	return 3


#########################################################################
####                              NAIVE AI                           ####
#########################################################################

import random

def get_AI_orders(game, player_id):
	"""Return orders of AI.

	Parameters
	----------
	game: game data structure (dict)
	player_id: player id of AI (int)

	Returns
	-------
	orders: orders of AI (str)

	"""

	orders = ''
	graze_orders = ''
	if canAppear(game, player_id):
		orders += 'sheep'
	for sheep in game['sheep_player' + str(player_id)]:
		w_attack = where_attack(game, sheep['position'])
		if w_attack != [0, 0]:
			orders += ' ' + str(sheep['position'][0]) + '-' + str(sheep['position'][1]) + ':x' + str(w_attack[0]) + '-' + str(w_attack[1])

	for sheep in game['sheep_player' + str(player_id)]:
		w_move = where_move(game, sheep['position'], player_id)
		if w_move != [0, 0]:
			orders += ' ' + str(sheep['position'][0]) + '-' + str(sheep['position'][1]) + ':@' + str(w_move[0]) + '-' + str(w_move[1])
			player = is_grass_on(game, w_move)
			if player != player_id and player:
				graze_orders +=  ' ' + str(w_move[0]) + '-' + str(w_move[1]) + ':*'
	orders += graze_orders
	return orders.strip()

def where_move(data, position, player_id):
	""" Determine where the AI Naive will choose to move on the game board.
	create a list of availables moves
	return a random move in the list of availables moves.

	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
		    -'sheep_player1': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            -'sheep_player2': A list of dictionaries representing a player's sheep with these hit point of life and its position
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.

	position : list of int
        The position on the game board of the sheep. Should be a list of two integers representing row and column indices.

	Returns
    -------
    int
        Returns:
            - [0, 0] if the sheep can't move.
            - list of int if the sheep can move.

    Version
    -------
    specification: Alessandro Morici (v.1 21/03/24)
	"""
	test_position = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
	available_position = []
	for test in test_position:
		position_to = [test[0] + position[0], test[1] + position[1]]
		if canMove(data, position, position_to, player_id):
			available_position.append(position_to)
	if len(available_position):
		return available_position[random.randint(0, len(available_position) - 1)]
	return [0, 0]

def where_attack(data, position):
	""" Determine where the AI Naive will choose to attack on the game board.

	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
		    -'sheep_player1': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            -'sheep_player2': A list of dictionaries representing a player's sheep with these hit point of life and its position
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.

	position : list of int
        The position on the game board of the sheep. Should be a list of two integers representing row and column indices.

	Returns
    -------
    int
        Returns:
            - [0, 0] if the sheep can't attack.
            - list of int if the sheep can attack.

    Version
    -------
    specification: Alessandro Morici (v.1 21/03/24)
	"""
	test_position = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
	for test in test_position:
		position_to = [test[0] + position[0], test[1] + position[1]]
		if is_sheep_on(data, position_to):
			return position_to
	return [0, 0]

#########################################################################
####                                DATA                             ####
#########################################################################

def getData(map_path):
	""" create data from .bsh file

	Paramaters
	----------
	map_path: path to the file .bsh (str)

	Return
	------
	data : dict
	    A dictionary containing information about the game board.
	    It should have the following keys:
	        - 'rock': A list of tuple representing the positions of all the rocks on the game board.
	        - 'map_size': A tuple of int representing the size of the game board.
	        - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
	        - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
	        - 'seed': A list of tuple representing the positions of all the seeds on the game board.
	        - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
	        - 'grass_player2': A list of dictionaries representing grass belonging to player 2.

	Version
    -------
    specification: Alessandro Morici (v.2 1/03/24)
	"""
	data = {
		"sheep_player1" :  [], # "sheep_player1" : [{"life": l, "position": [x, y] }],
		"sheep_player2" :  [],
		"rock": [], # "rock": [[x_1, y_1],[x_2, y_2],[x_3, y_3]],
		"seed": [], # "seed": [[x_1, y_1],[x_2, y_2],[x_3, y_3]],
		"grass_player1": [], # "grass_player1": [{"time": x, "level": x, “position”: [x, y] }],
		"grass_player2": [],
		"spawn_player1": [0, 0],
		"spawn_player2": [0, 0],
		"attack_log": {'player':0, 'position':[0, 0]},
		"map_size": (0, 0)
	}
	with open(map_path, 'r') as bsh:
		step = ""
		for line in bsh:
			l = line.split('\n')[0]
			if "map:" == l or "spawn:" == l or "seeds:" == l or "rocks:" == l:
				step = l
			elif step == "map:":
				size = l.split(' ')
				data['map_size'] = (int(size[0]), int(size[1]))
			elif step == "spawn:":
				n,x,y = l.split(' ')
				data['spawn_player'+str(n)] = [int(x), int(y)]
			elif step == "seeds:":
				x,y = l.split(' ')
				data['seed'].append([int(x), int(y)])
			elif step == "rocks:":
				x,y = l.split(' ')
				data['rock'].append([int(x), int(y)])
	return data

def copy_data(data):
	""" Create a copy of data.
	we can't import copy so we had to create one
	Parameters
	----------
	data : dict
	    A dictionary containing information about the game board.
	    It should have the following keys:
	        - 'rock': A list of tuple representing the positions of all the rocks on the game board.
	        - 'map_size': A tuple of int representing the size of the game board.
	        - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
	        - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
	        - 'seed': A list of tuple representing the positions of all the seeds on the game board.
	        - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
	        - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
	Returns
	-------
	new_data: the same dict but with different addresses

    Version
    -------
    specification: Alessandro Morici (v.1 16/03/24)
	"""
	new_data = {
		"sheep_player1" :  [{'life': sheep['life'], 'position': sheep['position']} for sheep in data["sheep_player1"]],
		"sheep_player2" :  [{'life': sheep['life'], 'position': sheep['position']} for sheep in data["sheep_player2"]],
		"rock": [[x,y] for x,y in data["rock"]],
		"seed": [[x,y] for x,y in data["seed"]],
		"grass_player1": [{'time': grass['time'], 'position': grass['position']} for grass in data["grass_player1"]],
		"grass_player2": [{'time': grass['time'], 'position': grass['position']} for grass in data["grass_player2"]],
		"spawn_player1": data["spawn_player1"],
		"spawn_player2": data["spawn_player2"],
		"attack_log": data['attack_log'],
		"map_size": data["map_size"]
	}
	return new_data

#########################################################################
####                              ORDER                              ####
#########################################################################

def execute_orders_step_by_step(data, orders):
	""" execute all orders

	Parameters
	----------
	data : dict
	    A dictionary containing information about the game board.
	    It should have the following keys:
	        - 'rock': A list of tuple representing the positions of all the rocks on the game board.
	        - 'map_size': A tuple of int representing the size of the game board.
	        - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
	        - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
	        - 'seed': A list of tuple representing the positions of all the seeds on the game board.
	        - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
	        - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
	Returns
	-------
	data: modified data structure
	"""
	# Appear step P1
	data = execute_orders(data, orders['player1_formated'], 'appear', 1)
	# Appear step P2
	data = execute_orders(data, orders['player2_formated'], 'appear', 2)
	# Attack step P1
	data = execute_orders(data, orders['player1_formated'], 'attack', 1)
	# Attack step P2
	data = execute_orders(data, orders['player2_formated'], 'attack', 2)
	# Move step P1
	data = execute_orders(data, orders['player1_formated'], 'move', 1)
	# Move step P2
	data = execute_orders(data, orders['player2_formated'], 'move', 2)
	# Graze step P1
	data = execute_orders(data, orders['player1_formated'], 'graze', 1)
	# Graze step P2
	data = execute_orders(data, orders['player2_formated'], 'graze', 2)
	return data

def execute_orders(data, player_orders, type_order, player_id):
	""" Execute all orders of a specific type that a specific player has sent

	Parameters
	----------
	data : dict
	    A dictionary containing information about the game board.
	    It should have the following keys:
	        - 'rock': A list of tuple representing the positions of all the rocks on the game board.
	        - 'map_size': A tuple of int representing the size of the game board.
	        - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
	        - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
	        - 'seed': A list of tuple representing the positions of all the seeds on the game board.
	        - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
	        - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
	players_orders: list of orders
	type_order: str 
		It represent the type of order to execute (move, attack, graze, appear)
	player_id: int
		It represent the id of the player for who the order will be executed

	Returns
	-------
	cdata: data modified after the execution of the orders
	"""
	cdata = copy_data(data)
	for order in player_orders:
		if type_order == order['cmd']:
			if type_order == 'attack':
				cdata = attackSheep(cdata, order['from'], order['to'], player_id)
			elif type_order == 'move':
				cdata = moveSheep(cdata, order['from'], order['to'], player_id)
			elif type_order == 'graze':
				cdata = grazeSheep(cdata, order['from'], player_id)
			elif type_order == 'appear':
				cdata = appearSheep(cdata, player_id)
	return cdata

def order_format_verif(order):
	""" Translate an order in json format.

	Parameters
	----------
	order : string
		A string containing an action to execute on the game board.

	Returns
    -------
    command : dict
    	A dictionary containing information about the action to execute on the game board.
    	It has the following keys:
    	- 'cmd': string representing the type of action to execute on the game board. ex: attack, move, graze, appear
    	- 'from': list of int representing the position from where the action begin.
    	- 'to': list of int representing the position from where the action end.

    Version
    -------
    specification: Alessandro Morici (v.1 7/03/24)
	"""
	command = {
		'cmd': 'none',
		'from': [0, 0],
		'to': [0, 0]
		}
	position_from = ''
	position_to = ''
	if len(order.split(':x')) == 2:
		command['cmd'] = 'attack'
		position_from = order.split(':x')[0]
		position_to = order.split(':x')[1]
	elif len(order.split(':@')) == 2:
		command['cmd'] = 'move'
		position_from = order.split(':@')[0]
		position_to = order.split(':@')[1]
	elif len(order.split(':')) == 2 and order.split(':')[1] == '*':
		position_from = order.split(':')[0]
		command['cmd'] = 'graze'
	elif order == 'sheep':
		command['cmd'] = 'appear'

	if command['cmd'] != 'appear' and command['cmd'] != 'none' and len(position_from.split('-')) == 2:
		try:
			command['from'][0] = int(position_from.split('-')[0])
			command['from'][1] = int(position_from.split('-')[1])
			if len(position_to.split('-')) == 2:
				command['to'][0] = int(position_to.split('-')[0])
				command['to'][1] = int(position_to.split('-')[1])
			elif command['cmd'] == 'move' or command['cmd'] == 'attack':
				command = {'cmd': 'none', 'from': [0, 0], 'to': [0, 0]}
				return command
		except ValueError:
			command = {'cmd': 'none', 'from': [0, 0], 'to': [0, 0]}
			return command
	return command

#########################################################################
####                           AUTO ACTION                           ####
#########################################################################

def growGrass(data, player):
	"""
    Make grass expand and update their life time
	
	Parameters 
	----------
	data : dict
        A dictionary containing information about the game board.
        It should have the following keys:
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.

    player : The attacking player (int: 1 OR 2)

	Return
	------
	data: modified game board (dict)

	Notes
	-----
	that should be called every turn
    
    VERSION 
    -------
    specification: Al-Bayati Ahmed v.1 25/02/24
	"""
	for grass in range(len(data['grass_player' + str(player)])):
		data['grass_player' + str(player)][grass]['time'] += 1
		if data['grass_player' + str(player)][grass]['time'] == 11:
			p = data['grass_player' + str(player)][grass]['position']
			case = [[p[0]+1, p[1]],[p[0]-1, p[1]],[p[0], p[1]+1],[p[0], p[1]-1]]
			for c in case:
				if canGrow(data, c):
					for seed in range(len(data['seed'])):
						if data['seed'][seed] == c:
							del data['seed'][seed]
					data['grass_player' + str(player)].append({"time": 1, "position": [c[0], c[1]]})
	return data

#########################################################################
####                              ACTION                             ####
#########################################################################

def grazeSheep(data, position, player):
	""" Make a sheep eat grass

	Parameters:
	----------
	data : dict
	    A dictionary containing information about the game board.
	    It should have the following keys:
	        - 'rock': A list of tuple representing the positions of all the rocks on the game board.
	        - 'map_size': A tuple of int representing the size of the game board.
	        - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
	        - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
	        - 'seed': A list of tuple representing the positions of all the seeds on the game board.
	        - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
	        - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
	position: position of the sheep ([int, int])
	player: number of player who is playing (int)

	Return:
	------ 
	data: modified game board or not (dict)

	Version:
	-------
	specification: Teto mbah russel anderson(v.2 16/03/2024)
	"""
	player_ennemi = player % 2 + 1
	if is_sheep_on(data, position) != player:
		return data
	cdata = copy_data(data)
	for i in range(len(cdata['grass_player'+str(player_ennemi)])):
		if cdata['grass_player'+str(player_ennemi)][i]['position'] == position:
			del cdata['grass_player'+str(player_ennemi)][i]
			return cdata
	for i in range(len(cdata['grass_player'+str(player)])):
		if cdata['grass_player'+str(player)][i]['position'] == position:
			del cdata['grass_player'+str(player)][i]
			return cdata
	return cdata

def moveSheep(data, position_from, position_to, player):
	"""   manage the movement of sheep by checking whether the order is legal to carry it out or not

	Parameters:
	----------
	data : dict
	    A dictionary containing information about the game board.
	    It should have the following keys:
	        - 'rock': A list of tuple representing the positions of all the rocks on the game board.
	        - 'map_size': A tuple of int representing the size of the game board.
	        - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
	        - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
	        - 'seed': A list of tuple representing the positions of all the seeds on the game board.
	        - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
	        - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
	position_from: where is the sheep ([int, int])
	position_to: where the sheep is going ([int, int])
	player:  number of player who is playing (int)

	Return:
	------
	data: modified game board data or not (dict)

	Version:
	-------
	specification: Teto mbah russel anderson(v.2 16/03/2024)
	"""
	if not canMove(data, position_from, position_to, player):
		return data
	cdata = copy_data(data)
	for i in range(len(data['sheep_player'+str(player)])):
		if cdata['sheep_player'+str(player)][i]['position'] == position_from:
			cdata['sheep_player'+str(player)][i]['position'] = position_to
			for seed in range(len(cdata['seed'])):
				if cdata['seed'][seed] == position_to:
					del cdata['seed'][seed]
					cdata['grass_player'+str(player)].append({"time": 1, "position": position_to})
					return cdata
			return cdata
	return cdata

def appearSheep(data, player):
	""" Make sheep appear on a spawn point

	Parameters
	----------
	data : dict
	    A dictionary containing information about the game board.
	    It should have the following keys:
	        - 'rock': A list of tuple representing the positions of all the rocks on the game board.
	        - 'map_size': A tuple of int representing the size of the game board.
	        - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
	        - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
	        - 'seed': A list of tuple representing the positions of all the seeds on the game board.
	        - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
	        - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
	n: player who is playing (int)

	Return
	------
	data: modified game board or not

	Version:
	-------
	specification: Teto mbah russel anderson(v.2 16/03/2024)
	"""
	if not canAppear(data, player):
		return data
	cdata = copy_data(data)
	cdata['sheep_player'+str(player)].append({"life": 3, "position": cdata['spawn_player'+str(player)]}) # ajoute de mouton
	return cdata

def attackSheep(data, position_from, position_to, player):
	""" This function allows a player to attack their enemy with their sheep.


	PARAMETERS 
	----------
	data : dict
	    A dictionary containing information about the game board.
	    It should have the following keys:
	        - 'rock': A list of tuple representing the positions of all the rocks on the game board.
	        - 'map_size': A tuple of int representing the size of the game board.
	        - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
	        - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
	        - 'seed': A list of tuple representing the positions of all the seeds on the game board.
	        - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
	        - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
	position0: The initial position of player X (liste)
	position1: The final position, the goal that we want to reach (liste)
	player : The attacking player (int: 1 OR 2)

	RETURNS 
	-------
	data: modified game board or not

	VERSION 
	-------    
		specification: Al-Bayati Ahmed v.1 25/02/24

	"""
	player_ennemi = player % 2 + 1
	if not canAttack(data, position_from, position_to) and data['attack_log']['position'] != position_from:
		return data

	for i in range(len(data['sheep_player'+str(player_ennemi)])):
		if data['sheep_player'+str(player_ennemi)][i]['position'] == position_to:
			data['attack_log'] = {'position': position_to, 'player': player % 2 + 1}
			data['sheep_player'+str(player_ennemi)][i]['life'] -= 1
			w_eject = where_eject_sheep(position_to, position_from, data)
			if w_eject == [0,0] or data['sheep_player'+str(player_ennemi)][i]['life'] == 0:
				del data['sheep_player'+str(player_ennemi)][i]
				return data
			data['sheep_player'+str(player_ennemi)][i]['position'] = w_eject
			return data
	return data

#########################################################################
####                           ACTION TOOLS                          ####
#########################################################################

def canGrow(data, position):
	""" Determine if a grass can grow at the specified position on the game board.
	grass can only grow on the board.
	grass can not grow on spawnpoints, on rock, on seed or on another grass. 
	
	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
	
	position : list of int
        The position on the game board to check if a grass can grow. Should be a list of two integers representing row and column indices.

	Returns
    -------
    int
        Returns:
            - False if grass can not grow at the specified position.
            - True if a grass can grow at the specified position.

    Version
    -------
    specification: Alessandro Morici (v.1 7/03/24)
	"""
	if not is_position_on_board(data, position):
		return False

	if is_spawnpoint_on(data, position):
		return False

	if is_rock_on(data, position):
		return False

	#if is_seed_on(data, position):
		#return False

	if is_grass_on(data, position):
		return False

	return True

def canAppear(data, player):
	"""Check if a player can appear a sheep on the game board.
	this impossible if:
	-there is already another sheep on the spawn
	-the number of grass square is insufficient 
	
	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
		    -'sheep_player1': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            -'sheep_player2': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
	
	player: player number (list of int)
	
	Returns:
            - False if he can not appear a sheep at the specified position.
            - True if he can appear a sheep at the specified position.
	
    Version
    -------
    specification: TETO MBAH RUSSEL ANDERSON (v.1 10/03/24)
    """
	if is_sheep_on(data, data['spawn_player'+str(player)]):
		return False

	#         actual number of sheep         >=         maximum number of sheep
	if len(data['sheep_player'+str(player)]) >= 1 + len(data['grass_player'+str(player)]) // 30:
		return False

	return True

def canMove(data, position_from, position_to, player):
	"""Check if a sheep can move at the specified position on the game board.
	This is impossible if the player:  
	-gives an illegal order(wrong format of the order, dirrection outside the board)
	-go on a rock
	-go on a spawn
	-it goes to another sheep
	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
		    -'sheep_player1': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            -'sheep_player2': A list of dictionaries representing a player's sheep with these hit point of life and its position
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
	position_from: starting possition of the player
	postition_to: player arrival position
	player: numbre of player (list of int)
	
	Returns:
            - False if sheep can not move at the specified position.
            - True if a sheep can move at the specified position.	

    Version:
    -------
    specification: TETO MBAH RUSSEL ANDERSON (v.1 10/03/24)
	"""
	if not is_position_on_board(data, position_to):
		return False

	if abs(position_from[0] - position_to[0]) > 1 or abs(position_from[1] - position_to[1]) > 1:
		return False

	if is_rock_on(data, position_to):
		return False
		
	if is_spawnpoint_on(data, position_to):
		return False

	if is_sheep_on(data, position_to):
		return False

	if is_sheep_on(data, position_from) != player:
		return False

	return True

def canAttack(data, position_from, position_to):
	""" This function's role is to indicate whether an attack is possible or not.   

    PARAMETERS 
    ----------
    data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
		    -'sheep_player1': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            -'sheep_player2': A list of dictionaries representing a player's sheep with these hit point of life and its position
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'attack_log': dict
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.

    position_from : The starting position of the sheep intending to attack (liste)

    position_to : The finale position of the sheep intending to attack (liste)


    RETURNS 
    ---------
    True or False depend of the situation (bool)

    VERSION 
    ---------
    specification: Al-Bayati Ahmed v.1 25/02/24
    """
	if abs(position_from[0] - position_to[0]) > 1 or abs(position_from[1] - position_to[1]) > 1:
		return False

	player_id_from = is_sheep_on(data, position_from)

	if not player_id_from and data['attack_log']['position'] != position_from:
		return False

	player_id_to = is_sheep_on(data, position_to)

	if not player_id_to:
		return False

	if player_id_to == player_id_from or data['attack_log']['player'] == player_id_to:
		return False

	return True

def where_eject_sheep(position_attacked_sheep, position_sheep_who_attack, data):
	"""
	This function determines the position where an attacked sheep would be ejected baseed on the attacker's sheep position while avoiding others sheeps, spawns, rocks and taking into account the boundaries of the game board.

	PARAMETERS
	----------

	position_attacked_sheep: The position of the sheep being attacked (list)
	position_sheep_who_attack: The position of the sheep attacking (list)
	data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
		    -'sheep_player1': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            -'sheep_player2': A list of dictionaries representing a player's sheep with these hit point of life and its position
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.

	RETURN
	------
	provisional_position : the final position of the sheep being ejected (liste)

	[0, 0] : If the sheep dies during the ejection.(liste)

	VERSION 
	-------
	specification: Al-Bayati Ahmed v.1 25/02/24

	"""
	vector_director = (position_attacked_sheep[0] - position_sheep_who_attack[0], position_attacked_sheep[1] - position_sheep_who_attack[1])
	provisional_position = [position_attacked_sheep[0] + vector_director[0] * 4, position_attacked_sheep[1] + vector_director[1] * 4]
	while is_sheep_on(data, provisional_position) or is_spawnpoint_on(data, provisional_position):
		provisional_position[0] += vector_director[0]
		provisional_position[1] += vector_director[1]
	if not is_position_on_board(data, provisional_position):
		return [0, 0]
	if is_rock_on(data, provisional_position):
		return [0, 0]
	return provisional_position

#########################################################################
####                           BASIC CHECK                           ####
#########################################################################

def is_rock_on(data, position):
	""" Determine if there is a rock at the specified position on the game board.

	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following key:
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.

	position : list of int
        The position on the game board to check for rock. Should be a list of two integers representing row and column indices.

	Returns
    -------
    int
        Returns:
            - False if there is no rock at the specified position.
            - True if there is a rock at the specified position.

    Version
    -------
    specification: Alessandro Morici (v.1 7/03/24)
	"""
	for r in data['rock']:
		if r == position:
			return True
	return False

def is_seed_on(data, position):
	""" Determine if there is a seed at the specified position on the game board.

	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following key:
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.

	position : list of int
        The position on the game board to check for seed. Should be a list of two integers representing row and column indices.

	Returns
    -------
    int
        Returns:
            - False if there is no seed at the specified position.
            - True if there is a seed at the specified position.

    Version
    -------
    specification: Alessandro Morici (v.1 7/03/24)
	"""
	for r in data['seed']:
		if r == position:
			return True
	return False

def is_spawnpoint_on(data, position):
	""" Determine if there is a spawnpoint at the specified position on the game board.

	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.

	position : list of int
        The position on the game board to check for spawnpoint. Should be a list of two integers representing row and column indices.

	Returns
    -------
    int
        Returns:
            - False if there is no spawnpoint at the specified position.
            - True if there is a spawnpoint at the specified position.

    Version
    -------
    specification: Alessandro Morici (v.1 7/03/24)
	"""
	if data["spawn_player1"] == position or data["spawn_player2"] == position:
		return True
	return False

def is_position_on_board(data, position):
	""" Determine if the specified position is on the game board.

	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following key:
            - 'map_size': A tuple of int representing the size of the game board.

	position : list of int
        The position to check. Should be a list of two integers representing row and column indices.

	Returns
    -------
    int
        Returns:
            - False if the specified position is not on the game board.
            - True if the specified position is on the game board.

    Version
    -------
    specification: Alessandro Morici (v.1 7/03/24)
	"""
	if position[0] < 1 or position[1] < 1 or position[0] > data['map_size'][0] or position[1] > data['map_size'][1]:
		return False
	return True

def is_grass_on(data, position):
	""" Determine if there is grass at the specified position on the game board.

	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
        Each dictionary in the lists should have a 'position' key indicating the position of the sheep on the game board.

	position : list of int
        The position on the game board to check for grass. Should be a list of two integers representing row and column indices.

	Returns
    -------
    int
        Returns:
            - 0 if there is no grass at the specified position.
            - 1 if there is grass belonging to player 1 at the specified position.
            - 2 if there is grass belonging to player 2 at the specified position.

    Version
    -------
    specification: Alessandro Morici (v.1 7/03/24)
	"""
	for g in data['grass_player1']:
		if g['position'] == position:
			return 1
	for g in data['grass_player2']:
		if g['position'] == position:
			return 2
	return 0

def is_sheep_on(data, position):
	""" Determine if there is a sheep at the specified position on the game board.
	
	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
            - 'sheep_player1': A list of dictionaries representing sheep belonging to player 1.
            - 'sheep_player2': A list of dictionaries representing sheep belonging to player 2.
        Each dictionary in the lists should have a 'position' key indicating the position of the sheep on the game board.

	position : list of int
        The position on the game board to check for a sheep. Should be a list of two integers representing row and column indices.

	Returns
    -------
    int
        Returns:
            - 0 if there is no sheep at the specified position.
            - 1 if there is a sheep belonging to player 1 at the specified position.
            - 2 if there is a sheep belonging to player 2 at the specified position.

    Version
    -------
    specification: Alessandro Morici (v.1 7/03/24)
    """
	for s in data['sheep_player1']:
		if s['position'] == position:
			return 1
	for s in data['sheep_player2']:
		if s['position'] == position:
			return 2
	return 0

#########################################################################
####                                UI                               ####
#########################################################################

def printData(term, data, winner=0):
	""" this function will print all the things needed to be shown on the board :
	sheep player 1
	sheep  player 2
	seeds
	rocks
	grasse level 1
	grasse level 2
	grasse player 1
	grasse player 2
	spawn points
	

	Parameters
	----------
	term: (blessed.Terminal())
	data (dict):  dictionary containing information about the game board.
            It should have the following keys:
		    -'sheep_player1': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            -'sheep_player2': A list of dictionaries representing a player's sheep with these hit point of life and its position
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.
            - 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
            - 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
            - 'seed': A list of tuple representing the positions of all the seeds on the game board.
            - 'grass_player1': A list of dictionaries representing grass belonging to player 1.
            - 'grass_player2': A list of dictionaries representing grass belonging to player 2.
    winner : is an aptionnal parameter and only useful a the and because it shows who on the board


	  Version
    -------
    specification: Awan Muhammad Ammar (v.4 22/03/24)
	"""
	for x in range(1, data['map_size'][0] + 1):
		for y in range(1, data['map_size'][1] + 1):
			if not is_rock_on(data, [x, y]) and not is_seed_on(data, [x, y]):
				print_char_at('  ', [x, y], term, data)

	# put the rocks
	for r in data['rock']:
		print_char_at('🪨', r, term, data)

	# put the seeds
	for s in data['seed']:
		print_char_at('🌱', s, term, data)

	for grass in data['grass_player1']:
		print_char_at(term.on_yellow + ' ', grass['position'], term, data)
	for grass in data['grass_player2']:
		print_char_at(term.on_skyblue + ' ', grass['position'], term, data)

	# put the spawns points
	print_char_at(term.on_yellow + 's', data['spawn_player1'], term, data)
	print_char_at(term.on_skyblue + 's', data['spawn_player2'], term, data)

	for s in data["sheep_player1"]:
		print_char_at(term.on_yellow + '🐑', s['position'], term, data)

	for s in data["sheep_player2"]:
		print_char_at(term.on_skyblue + '🐑', s['position'], term, data)

	position = [data['map_size'][1] // 2, data['map_size'][1] + 1]
	score = 'score: ' + '         '
	print_char_at(score, position, term, data)
	score = 'score: ' + str(len(data['grass_player1'])) + ' - ' + str(len(data['grass_player2']))
	print_char_at(score, position, term, data)
	position = [data['map_size'][1] // 2 - 1, data['map_size'][1] + 1]
	if winner == 1:
		print_char_at('player1 WIN', position, term, data)
	elif winner == 2:
		print_char_at('player2 WIN', position, term, data)
	elif winner == 3:
		print_char_at('DRAW', position, term, data)

	position = [data['map_size'][0] + 1, 1]
	print_char_at('cmd> ', position, term, data)

#########################################################################
####                             UI TOOLS                            ####
#########################################################################

def render_grid(term, row, col):
	""" this function will print the grid of the game 

	Parameters
	----------
	term: (blessed.Terminal())
	row: number of row (int)
	col: number of col (int)

	Return
	------
	grid_rows: list of str
	
	 Version
    -------
    specification: Awan Muhammad Ammar (v.2 22/03/24)
	
	"""
	grid_rows = []
	for i in range(row + 1):
		if i != row:
			rows = ['', "│   " * col + "│"]
		else:
			rows = ['', '']
		for j in range(col):
		    if i == 0 and j == 0:
		        rows[0] += "┌───" #+ "─" * 3
		    elif i == 0 and j == col - 1:
		    	rows[0] += "┬───┐"
		    elif i == row and j == 0:
		    	rows[0] += "└───┴"
		    elif i == row and j == col - 1:
		    	rows[0] += "───┘"
		    elif i == row:
		    	rows[0] +=  "───┴"
		    elif j == 0:
		        rows[0] += "├───"
		    elif i == 0:
		        rows[0] += "┬───"
		    elif j == col - 1:
		    	rows[0] += "┼───┤"
		    else:
		        rows[0] += "┼───"
		grid_rows.append(rows[0])
		grid_rows.append(rows[1])
	return grid_rows

def print_grid(term, data):
	"""this function will get us the center , will print the grid and numbers the line 1 to 20
	
	parameters
	----------
	term  : (blessed.Terminal())
    data : dict
		A dictionary containing information about the game board.
        It should have the following keys:
		    -'sheep_player1': A list of dictionaries representing a player's sheep with these hit point of life and its position 
            -'sheep_player2': A list of dictionaries representing a player's sheep with these hit point of life and its position
            - 'rock': A list of tuple representing the positions of all the rocks on the game board.
            - 'map_size': A tuple of int representing the size of the game board.

	 Version
    -------
    specification: Awan Muhammad Ammar (v.3 22/03/24)
	 
	 """
	# get center
	cr = int(term.height/2)
	cc = int(term.width/2)

	# print the grid
	grid = render_grid(term, data['map_size'][0], data['map_size'][1])
	l = 0
	for i in grid:
		print(term.move_yx(cr - data['map_size'][0] + l, cc - data['map_size'][1]*2) + '\033[0;37;40m' + i, end='', flush=True)
		l += 1
	# numerotation ligne et colonne
	for i in range(data['map_size'][1] + 1):
		print_char_at(str(i), [0, i], term, data)
	for i in range(1, data['map_size'][0] + 1):
		print_char_at(str(i), [i, 0], term, data)

def print_char_at(char, position, term, data):
	""" print a str at a specified position on the game board

	parameters
	----------
	char : a chaine of utf8 character
	position : postion of the thing ojn board the board
	term : (blessed.Terminal())
	data : the data structure of the game that we made 

	"""
	cr = int(term.height/2)
	cc = int(term.width/2)
	pixel_position = [cr - data['map_size'][0] + position[0]*2 - 1, cc - (data['map_size'][1] - position[1]*2 + 1) * 2]
	print(term.move_yx(pixel_position[0], pixel_position[1]) + char + term.normal, end='', flush=True)


# TEST

play_game('carte.bsh', 1, 'AI', '127.0.0.1', 2, 'AI', '127.0.0.1')


# group 15

#play_game('carte.bsh', 15, 'remote', '138.48.160.146', 16, 'AI', '127.0.0.1')


# groupe 11

#play_game('carte.bsh', 1, 'AI', '127.0.0.1', 2, 'remote', '138.48.160.154')

#groupe 10

#play_game('carte.bsh', 16, 'AI', '127.0.0.1', 10, 'remote', '138.48.160.185')