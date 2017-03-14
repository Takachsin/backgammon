from pprint import pprint
#import numpy as np
#import tensorflow as tf
#import matplotlib.pyplot as plt

# set constants
learning_rate = 0.5
discount_factor = 0.5
doubling_cube_values = [1, 2, 4, 8, 16, 32, 64]

# Calculate the number of spaces remaining to bear off all checkers
def calc_pip_count():
    doubling_cube_value = find_doubling_cube_value()
    player_pip = 0
    opponent_pip = 0
    board = gnubg.board()
    opponent_board, player_board = board
    for x in range (0,24):
        player_pip = player_pip + player_board[x] * (x+1)
    for x in range (0,24):
        opponent_pip = opponent_pip + opponent_board[x] * (x+1)
    if player_pip > opponent_pip:
        reward = 1 * doubling_cube_value
    elif player_pip < opponent_pip:
        reward = -1 * doubling_cube_value
    else:
        reward = 0
    return player_pip, opponent_pip, reward;

# Determines if a player is bearing off based on the chip positions
def determine_bearing_off():
    board = gnubg.board()
    opponent_board, player_board = board

    # uses [6:] to skip checking the checkers in the bearing off zone
    player_bearing_off = all(item == 0 for item in player_board[6:])
    opponent_bearing_off = all(item == 0 for item in opponent_board[6:])
    return player_bearing_off, opponent_bearing_off;

# Decides whether to double
def decide_on_double():
    # Calculate probability of winning
    evaluate = gnubg.evaluate()
    prob_of_winning = evaluate[0]

    if prob_of_winning > 0.5:
        double = True
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

# initialize values
total_reward = 0
reward = 0
state = 0

# Check score from last game to determine if a game has completed
match = gnubg.match()
past_player_score = match['games'][-1]['info']['score-O']
past_opponent_score = match['games'][-1]['info']['score-X']

while True:
    posinfo = gnubg.posinfo()
    cubeinfo = gnubg.cubeinfo()
    match = gnubg.match()

    player_score = match['games'][-1]['info']['score-O']
    opponent_score = match['games'][-1]['info']['score-X']
    player_pip, opponent_pip, reward = calc_pip_count()
    total_reward += reward

    # Breaks the loop when a winner has been determined
    if player_score != past_player_score or opponent_score != past_opponent_score:
        winner = match['games'][-1]['info']['winner']
        if player_score > past_player_score:
            player_has_won = True
        if opponent_score > past_opponent_score:
            player_has_won = False
        print("Game Completed!")
        break;

    # Decides whether to accept the oppoent's double
    opponent_doubled = posinfo['doubled']
    if opponent_doubled:
        double = decide_on_double()
        if double:
            print("Player accepts double.")
            gnubg.command('accept')
        else:
            print("Player rejects double, and loses match.")
            player_has_won = False
            gnubg.command('reject')
            break;

    # Cubeowner = 0 if opponent, -1 if no one, 1 if player
    opponent_has_cube = cubeinfo['cubeowner'] == 0

    players_turn = posinfo['turn']

    # Decides whether player should double before rolling
    double = decide_on_double()
    if players_turn and double and not opponent_has_cube:
        total_reward += reward
        gnubg.command('double')

    # Accepts the resignation when the opponent offers to resign
    opponent_resigns = posinfo['resigned']
    if opponent_resigns:
        print("Opponent resigns!")
        player_wins_game = True
        gnubg.command('accept')
        break;

    # Checks to make sure the player has not rolled yet
    die_1, die_2 = posinfo['dice']
    if die_1 == 0 and die_2 == 0:
        gnubg.command('roll')

    # Checks if a move is possible
    die_1, die_2 = posinfo['dice']
    if players_turn and die_1 > 0 and die_2 > 0:
        gnubg.command('move ' + gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()), gnubg.board()))
        #gnubg.command(gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()),gnubg.board()))

    doubling_cube_value = cubeinfo["cube"]
    print(doubling_cube_value)

if player_has_won:
    print("Player has won the game!")
    reward = 1 * (doubling_cube_value + 1000)
else:
    print("Opponent has won the game!")
    reward = -1 * (doubling_cube_value + 1000)

total_reward += reward
print(total_reward)
