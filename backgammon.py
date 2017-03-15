from pprint import pprint

# ************Set Parameters*******************
learning_rate = 0.5
discount_factor = 0.5
doubling_cube_values = [1, 2, 4, 8, 16, 32, 64]
epochs = 1
matchto = 7
verbose = True
# *********************************************

# Calculate the number of spaces remaining to bear off all checkers
def calc_pip_count():
    player_pip = 0
    opponent_pip = 0
    board = gnubg.board()
    opponent_board, player_board = board
    for x in range (0,24):
        player_pip = player_pip + player_board[x] * (x+1)
    for x in range (0,24):
        opponent_pip = opponent_pip + opponent_board[x] * (x+1)
    return player_pip, opponent_pip

def calc_reward():
    player_pip, opponent_pip = calc_pip_count()
    doubling_cube_value = cubeinfo["cube"]
    if player_pip > opponent_pip:
        reward = 1 * doubling_cube_value
    elif player_pip < opponent_pip:
        reward = -1 * doubling_cube_value
    else:
        reward = 0
    return reward

# Determines if a player is bearing off based on the chip positions
def determine_if_game_has_ended():
    board = gnubg.board()
    opponent_board, player_board = board
    player_has_won = all(item == 0 for item in player_board)
    opponent_has_won = all(item == 0 for item in opponent_board)
    return player_has_won, opponent_has_won

# Determines if a player is bearing off based on the chip positions
def determine_bearing_off():
    board = gnubg.board()
    opponent_board, player_board = board

    # uses [6:] to skip checking the checkers in the bearing off zone
    player_bearing_off = all(item == 0 for item in player_board[6:])
    opponent_bearing_off = all(item == 0 for item in opponent_board[6:])
    return player_bearing_off, opponent_bearing_off

# Decides whether to double
def decide_on_double():
    # Calculate probability of winning
    evaluate = gnubg.evaluate()
    prob_of_winning = evaluate[0]

    if prob_of_winning > 0.5:
        double = True
    else:
        double = False
    return double

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
    return prob

def calc_Q(state, action, reward, next_state, next_action):
    #q = q + learning_rate * (reward + discount_factor * (max q_next_state - q)
    return

# decides whether to double or not based on policy derived from Q
def decide_action(state):
    # choose double based on policy derived from Q
    return double

for x in xrange(0, epochs):
    # Start the game
    if verbose: print("Starting Game " + str(x))
    gnubg.command('new match ' + str(matchto))

    # initialize values
    total_reward = 0
    reward = 0
    state = 0

    while True:
        # Breaks the loop when a winner has been determined
        player_has_won, opponent_has_won = determine_if_game_has_ended()
        if player_has_won or opponent_has_won:
            if verbose: print("Game Completed, woohoo!")
            break

        posinfo = gnubg.posinfo()
        cubeinfo = gnubg.cubeinfo()
        match = gnubg.match()

        player_score = match['games'][-1]['info']['score-O']
        opponent_score = match['games'][-1]['info']['score-X']
        opponent_doubled = posinfo['doubled']
        opponent_resigns = posinfo['resigned']
        opponent_has_cube = cubeinfo['cubeowner'] == 0
        die_1, die_2 = posinfo['dice']
        player_pip, opponent_pip = calc_pip_count()
        total_reward += reward

        # Decides whether to accept the oppoent's double
        if opponent_doubled:
            double = decide_on_double()
            if double:
                if verbose: print("Player accepts double.")
                gnubg.command('accept')
            else:
                if verbose: print("Player rejects double, and loses match.")
                gnubg.command('reject')
                break
        # Accepts the resignation when the opponent offers to resign
        elif opponent_resigns:
            if verbose: print("Opponent resigns!")
            gnubg.command('accept')
            break
        # Checks to make sure the player has not rolled yet
        elif die_1 == 0 and die_2 == 0:
            # Decides whether player should double before rolling
            double = decide_on_double()
            if double and not opponent_has_cube:
                total_reward += reward
                gnubg.command('double')
            gnubg.command('roll')
        else:
            gnubg.command('move ' + gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()), gnubg.board()))

        # Checks if a move is possible
        #die_1, die_2 = posinfo['dice']
        #if players_turn and die_1 > 0 and die_2 > 0:

            #gnubg.command(gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()),gnubg.board()))
        doubling_cube_value = cubeinfo["cube"]

    if player_has_won:
        if verbose: print("Player has won the game!")
        reward = 1 * (doubling_cube_value + 1000)
    else:
        if verbose: print("Opponent has won the game!")
        reward = -1 * (doubling_cube_value + 1000)

total_reward += reward
print(total_reward)
