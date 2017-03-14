from pprint import pprint
#import numpy as np
#import tensorflow as tf
#import matplotlib.pyplot as plt

# set constant rates
learning_rate = 0.5
discount_factor = 0

# Pulls the doubling cube information from GNUBG
def find_doubling_cube_value():
    cubeinfo = gnubg.cubeinfo()
    doubling_cube_value = cubeinfo["cube"]
    return doubling_cube_value;

# Calculate the number of spaces remaining to bear off all checkers
def calc_pip_count():
    doubling_cube_value = find_doubling_cube_value()
    player_pip = 0
    opponent_pip = 0
    board = gnubg.board()
    opponent_board, player_board = board
    for x in xrange (0,24):
        player_pip = player_pip + player_board[x] * (x+1)
    for x in xrange (0,24):
        opponent_pip = opponent_pip + opponent_board[x] * (x+1)
    if player_pip > opponent_pip:
        reward = 1 * doubling_cube_value
    elif player_pip < opponent_pip:
        reward = -1 * doubling_cube_value
    else:
        reward = 0
    return player_pip, opponent_pip, reward;

def determine_winner():
    board = gnubg.board()
    opponent_board, player_board = board
    player_count = all(player_board == 0 for item in board)
    opponent_count = all(opponent_board == 0 for item in board)
    return player_count, opponent_count;

def determine_winner_1():
    match = gnubg.match()
    match_info = match['games']
    return match_info[0]['info']['winner'];

# Decides whether to double
def decide_on_double():
    player_pip, opponent_pip, reward = calc_pip_count()
    if player_pip > opponent_pip:
        double = True
    elif player_pip < opponent_pip:
        double = False
    else:
        double = False
    return double;

# Defines the probability of rolling a specific number
def prob_of_rolling(num):
    total_combinations = 36
    prob = 0.00
    combinations = 0
    for die_1 in range(1,7):
        if die_1 == num:
            combinations += 1
    for die_2 in range(1,7):
        if die_2 == num:
            combinations += 1
    for die_1 in range(1,7):
        for die_2 in range(1,7):
            if (die_1 + die_2) == num:
                combinations += 1
    prob = combinations / float(total_combinations)
    return prob;

def calc_Q(state, action, reward, next_state, next_action):
    #q = q + learning_rate * (reward + discount_factor * (max q_next_state - q)
    return;

#Q(st, at) = Q(st, at) + alpha*(rt+gamma*max(Q(st+1, a) - Q(st, at)))
#SARSA - Q(st, at) = Q(st, at) + alpha*(rt+gamma*max(Q(st+1, at+1) - Q(st, at)))

# Start the game
print("Starting Game")
gnubg.command('new game')
#gnubg.command('show pipcount')

# initialize values
total_reward = 0
reward = 0
state = 0
doubling_cube_values = [1, 2, 4, 8, 16, 32, 64]

#print(prob_of_rolling(2))

# Testing
#cubeinfo = gnubg.posinfo()
#cube_owner = cubeinfo['dice'][0]
#pprint(cube_owner)
#print(type(cubeinfo))

#s: turn until game ends
#a: double, don't double, accept double, reject double

while True:
    posinfo = gnubg.posinfo()
    cubeinfo = gnubg.cubeinfo()

    player_pip, opponent_pip, reward = calc_pip_count()
    total_reward += reward

    #cubeinfo = gnubg.match()
    #cube_owner = cubeinfo["games"]
    #cubes = cube_owner[0]['game'] #action, dice, player
    #cubey = cubes[0]['action']
    #cubes = cube_owner[0]['info']['score-O'] #score-O, score-X, winner
    #pprint(cubey)

    # Decides whether to accept the oppoent's double
    opponent_doubled = posinfo['doubled']
    if opponent_doubled:
        double = decide_on_double()
        if double:
            print("Player accepts double.")
            gnubg.command('accept')
        else:
            print("Player rejects double, and loses match.")
            player_wins_game = False
            gnubg.command('reject')
            break;

    # Breaks the loop when a winner has been determined
    player_count, opponent_count = determine_winner()
    if player_count or opponent_count:
        print("Game Completed!")
        break;

    # Accepts the resignation when the opponent offers to resign
    opponent_resigns = posinfo['resigned']
    if opponent_resigns:
        print("Opponent resigns!")
        player_wins_game = True
        gnubg.command('accept')
        break;

    # Cubeowner = 1 if opponent, -1 if no one, 0 if player
    opponent_has_cube = cubeinfo['cubeowner'] == 1

    # Decides whether player should double before rolling
    double = decide_on_double()
    if double and not opponent_has_cube:
        total_reward += reward
        #gnubg.command('double')

    gnubg.command('roll')
    die_1 = posinfo['dice'][0]
    die_2 = posinfo['dice'][1]

    # Commands an optimal move if a move is possible
    players_turn = posinfo['turn']
    if players_turn and die_1 > 0 and die_2 > 0:
        gnubg.command('move ' + gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()), gnubg.board()))
        #gnubg.command(gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()),gnubg.board()))
    state += 1


doubling_cube_value = find_doubling_cube_value()

if True:#player_wins_game:
    reward = 1 * (doubling_cube_value + 1000)
else:
    reward = -1 * (doubling_cube_value + 1000)

total_reward += reward
print(total_reward)
