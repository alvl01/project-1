#-*- coding: utf-8 -*-

import math

# other functions
...
...
...



# main function - if necessary, other parameters can be used
def get_AI_orders(game, player_id):
	"""Return orders of AI.

	Parameters
	----------
	game: game data structure (dict)
	player_id: player id of AI (int)

	Returns
	-------
	orders: orders of AI (str)

	Version
	-------
	specification: Alessandro Morici (v.1 10/04/24)
	"""
	appear_order, cdata = get_appear_sheep_order(game, player_id)
	orders = appear_order

	is_order_before = False
	if orders != '':
		is_order_before = True

	attack_orders, cdata = get_attack_sheep_orders(cdata, player_id, is_order_before)
	orders += attack_orders

	if orders != '':
		is_order_before = True

	move_orders, cdata = get_move_sheep_orders(cdata, player_id, is_order_before)
	orders += move_orders

	if orders != '':
		is_order_before = True

	orders += get_graze_sheep_orders(cdata, player_id, is_order_before)

	return orders

#########################################################################
####                           TOOLS DEEP 0                          ####
#########################################################################

def get_appear_sheep_order(data, player_id):
	""" add the command sheep if a sheep can appear

	Parameters
	----------
	data : dict
		A dictionary containing information about the game board.
		It should have the following keys:
			- 'spawn_player1': A tuple of int representing the position of the spawnpoint belonging to player 1.
			- 'spawn_player2': A tuple of int representing the position of the spawnpoint belonging to player 2.
			- 'grass_player1': A list of dictionaries representing grass belonging to player 1.
			- 'grass_player2': A list of dictionaries representing grass belonging to player 2.

	player_id : int
	    The id of the current player

	Returns
	-------
	(str, {})
		str : is the command to send 
		cdata : is a copy of data that is modified

	Version
	-------
	specification: Awan Muhammad Ammar (v.1 18/04/24)
	"""
	if canAppear(data, player_id):
		cdata = appearSheep(data, player_id)
		return 'sheep', cdata
	return '', copy_data(data)

def get_attack_sheep_orders(data, player_id, is_order_before):
	""" for every sheep if the sheep can attack add a an odrer to attack

	Parameters
	----------
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

	player_id : int
		The id of the current player

	is_order_before : boolean
		define if this is the beginning of the orders

	Return
	------
	(str, {})
		str : is the command to add 
		cdata : is a copy of data that is modified

	VERSION 
	-------
	specification: Al-Bayati Ahmed v.1 (18/04/24)

	"""
	orders = ""
	already_attacked = []
	cdata = copy_data(data)
	for sheep in data['sheep_player' + str(player_id)]:
		next_squares = get_next_squares(sheep['position'])
		for square in next_squares:
			if canAttack(data, sheep['position'], square) and square not in already_attacked:
				already_attacked.append(square)
				new_position = where_eject_sheep(square, sheep['position'], data)
				orders += " " + str(sheep['position'][0]) + "-" + str(sheep['position'][1]) + ':x' + str(square[0]) + "-" + str(square[1])
				cdata = attackSheep(cdata, sheep['position'], square, player_id)

	if not is_order_before:
		orders = orders.strip()

	return orders, cdata

def get_move_sheep_orders(data, player_id, is_order_before):
	""" for every sheep get a orders to move

	Parameters
	----------
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

	player_id : int
		The id of the current player

	is_order_before : boolean
		define if this is the beginning of the orders

	Return
	------
	orders : is the command to add 

	Version:
	-------
	specification: Teto mbah russel anderson(v.1 20/04/2024)
	"""
	orders = ""
	cdata = copy_data(data)
	for sheep in data['sheep_player' + str(player_id)]:

		best_seed_value, seed = most_valuable_seed(data, sheep)

		best_grass_value, grass = most_valuable_grass(data, sheep, player_id)

		if best_grass_value >= best_seed_value or not best_seed_value:
			pos = get_next_position(data, sheep['position'], grass['position'], player_id)
		else:
			pos = get_next_position(data, sheep['position'], seed, player_id)

		if canMove(data, sheep['position'], pos, player_id):
			orders += " " + str(sheep['position'][0]) + "-" + str(sheep['position'][1]) + ':@' + str(pos[0]) + "-" + str(pos[1])
			cdata = moveSheep(cdata, sheep['position'], pos, player_id)

	if not is_order_before:
		orders = orders.strip()

	return orders, cdata

def get_graze_sheep_orders(data, player_id, is_order_before):
	""" if on ennemy grass order to eat it

	Parameters
	----------
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

	player_id : int
	    The id of the current player

	is_order_before : boolean
		define if this is the beginning of the orders

	Return
	------
	orders : is the command to add 

	Version:
	-------
	specification: Awan Muhammad Ammar(v.1 20/04/2024)
	"""
	orders = ""
	for sheep in data['sheep_player' + str(player_id)]:
		if is_grass_on(data, sheep['position']) == player_id % 2 + 1:
			orders += " " + str(sheep['position'][0]) + "-" + str(sheep['position'][1]) + ':*'

	if not is_order_before:
		orders = orders.strip()

	return orders

#########################################################################
####                           TOOLS DEEP 1                          ####
#########################################################################

def most_valuable_seed(data, sheep):
	""" get value of the nearest seed

	Parameters
	----------
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

	Returns
	-------
	Float:
		expension * 2/(distance + 1)

	Version:
	-------
	specification: Teto mbah russel anderson(v.1 20/04/2024)
	"""
	dist, seed = get_dist_to_closer_seed(data, sheep)
	if (seed == [0, 0]):
		return 0, seed
	return get_expension_number(data, seed) * 2 / (dist + 1), seed

# Manque spécification
def most_valuable_grass(game, sheep, player_id):
	"""
	Parameters
	----------
	game (dict):  dictionary containing information about the game board.
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
	
	sheep (dict): dictionary containing information about a sheep.
			It should have the following key:
			- 'position': A tuple of int representing the position of the sheep

	player_id : int
		The id of the current player

	Returns
	------
	(int, {})
		actual_value: value found (int)
		grass: grass found (dict)
	
	Version
	-------
	specification: Alessandro Morici (v.1 10/04/24)
	"""
	actual_value = -1
	actual_grass = {'position':[0, 0]}
	for grass in game['grass_player' + str(player_id % 2 + 1)]:
		new_value = get_value_ennemi_grass(game, grass, sheep)
		if actual_value < new_value:
			actual_value = new_value
			actual_grass = grass 
	return actual_value, actual_grass

def get_next_position(data, position_from, position_to, player_id):
	""" get the best next squares for a specified sheep and a specified destination

	Parameters
	----------
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

	position_from: ([int, int])

	position_to: ([int, int])	

	player_id : int
		The id of the current player

	Returns
	-------
	list of int:
		representing the position where the sheep should go

	Version
	-------
	specification: Alessandro Morici (v.1 10/04/24)
	"""
	dist = get_distance_between(position_from, position_to)
	next_positions = get_next_squares(position_from)
	next_positions = sorted(next_positions, key=lambda x: is_grass_on(data, x), reverse=True) # peut etre a changer
	test_moves = [pos for pos in next_positions if get_distance_between(pos, position_to) < dist]
	for move in test_moves:
		if canMove(data, position_from, move, player_id):
			return move
	test_moves = [pos for pos in next_positions if get_distance_between(pos, position_to) == dist]
	for move in test_moves:
		if canMove(data, position_from, move, player_id):
			return move
	return [0, 0]

#########################################################################
####                           TOOLS DEEP 2                          ####
#########################################################################

def get_dist_to_closer_seed(data, sheep):
	""" get the nearest seed information
	Parameters
	----------
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

	sheep (dict): dictionary containing information about a sheep.
			It should have the following key:
			- 'position': A tuple of int representing the position of the sheep
	Return
	------
	(int, {})
		actual_dist: distance between a spécified sheep and the found seed
		seed (dict): found seed

	Version:
	-------
	specification: Awan Muhammad Ammar(v.1 20/04/2024)
	"""
	actual_seed = [0, 0]
	actual_dist = 10000
	for seed in data['seed']:
		test_dist = get_distance_between(seed, sheep['position'])
		if actual_dist > test_dist:
			actual_seed = seed
			actual_dist = test_dist
	return actual_dist, actual_seed

def get_value_ennemi_grass(data, grass, sheep):
	""" get the value of a specified grass for a specified sheep

	Parameters
	----------
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

	grass (dict): dictionary containing information about a grass/
			It should have the following key:
			- 'position': A tuple of int representing the position of the grass

	sheep (dict): dictionary containing information about a sheep.
			It should have the following key:
			- 'position': A tuple of int representing the position of the sheep

	Return
	------
	Float: 
		the value that as been calculated

	Version
	-------
	specification: Alessandro Morici (v.1 10/04/24)
	"""
	if not is_grass_reachable(data, grass, sheep):
		return 0
	expension_value = get_expension_number(data, grass['position'])
	distance = get_distance_between(grass['position'], sheep['position'])
	return expension_value / (distance + 1)

#########################################################################
####                               BASIC                             ####
#########################################################################

def get_expension_number(data, position):
	""" get number of square a spécified grass will grow

	Parameters
	----------
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

	position : ([int, int])

	Return
	------
	int:
		number of squares

	Version
	-------
	specification: Alessandro Morici (v.1 10/04/24)
	"""
	value = 0
	next_squares = get_next_squares(position)
	for next_position in next_squares:
		if canGrow(data, next_position):
			value += 1
	return value

def is_grass_reachable(data, grass, sheep):
	""" define if a grass is reachable for a specified sheep before expension

	Parameters
	----------
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

	grass (dict): dictionary containing information about a grass/
			It should have the following key:
			- 'position': A tuple of int representing the position of the grass

	sheep (dict): dictionary containing information about a sheep.
			It should have the following key:
			- 'position': A tuple of int representing the position of the sheep

	Return
	------
	Boolean:
		True if the sheep will arrived before the expension
		False if the sheep won't arrived before the expension

	Version
	-------
	specification: Alessandro Morici (v.1 10/04/24)
	"""
	if 11 - grass['time'] >= get_distance_between(grass['position'], sheep['position']):
		return True
	return False

def get_distance_between(position1, position2):
	""" get distance between 2 points

	Parameters
	----------
	position1: ([int, int])
	position2: ([int, int])	

	Return
	------
	int:
		distance

	Version
	-------
	specification: Alessandro Morici (v.1 10/04/24)
	"""
	return max(abs(position1[0] - position2[0]), abs(position1[1] - position2[1]))

def get_next_squares(position):
	""" get position of the next to a specified position

	Parameters
	----------
	position: ([int, int])

	Return
	------
	list of list of int:
		list of postion next to the specified position

	Version
	-------
	specification: Alessandro Morici (v.1 10/04/24)
	"""
	next_vectors = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
	return [[position[0] + vector[0], position[1] + vector[1]] for vector in next_vectors]

#########################################################################
####                              IMPORT                             ####
#########################################################################

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
	if not canAttack(data, position_from, position_to):
		return data

	for i in range(len(data['sheep_player'+str(player_ennemi)])):
		if data['sheep_player'+str(player_ennemi)][i]['position'] == position_to:
			data['sheep_player'+str(player_ennemi)][i]['life'] -= 1
			w_eject = where_eject_sheep(position_to, position_from, data)
			if w_eject == [0,0] or data['sheep_player'+str(player_ennemi)][i]['life'] == 0:
				del data['sheep_player'+str(player_ennemi)][i]
				return data
			data['sheep_player'+str(player_ennemi)][i]['position'] = w_eject
			return data
	return data

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
	provisional_position = [position_attacked_sheep[0] + vector_director[0] * 5, position_attacked_sheep[1] + vector_director[1] * 5]
	while is_sheep_on(data, provisional_position) or is_spawnpoint_on(data, provisional_position):
		provisional_position[0] += vector_director[0]
		provisional_position[1] += vector_director[1]
	if not is_position_on_board(data, provisional_position):
		return [0, 0]
	if is_rock_on(data, provisional_position):
		return [0, 0]
	return provisional_position

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
















