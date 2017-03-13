from pprint import pprint

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
    temp1 = all(player_board == 0 for item in board)
    temp2 = all(opponent_board == 0 for item in board)
    return temp1, temp2;

def determine_winner_1():
    match = gnubg.match()
    match_info = match['games']
    return match_info[0]['info']['winner'];

def decide_on_double():
    player_pip, opponent_pip, reward = calc_pip_count()
    doubling_cube_value = find_doubling_cube_value()
    if player_pip > opponent_pip:
        double = True
        reward = 1 * doubling_cube_value
    elif player_pip < opponent_pip:
        double = False
        reward = -1 * doubling_cube_value
    else:
        double = False
        reward = 0
    return double;

# Defines the probability of rolling a specific number
def prob_of_rolling(num):
    total_combinations = 36
    prob = 0.00
    combinations = 0
    for die1 in range(1,7):
        if die1 == num:
            combinations += 1
    for die2 in range(1,7):
        if die2 == num:
            combinations += 1
    for die1 in range(1,7):
        for die2 in range(1,7):
            if (die1 + die2) == num:
                combinations += 1
    prob = combinations / float(total_combinations)
    return prob;

#Q(st, at) = Q(st, at) + alpha*(rt+gamma*max(Q(st+1, a) - Q(st, at)))
#SARSA - Q(st, at) = Q(st, at) + alpha*(rt+gamma*max(Q(st+1, at+1) - Q(st, at)))

# Start the game
print("Starting Game")
gnubg.command('new game')
#gnubg.command('show pipcount')
total_reward = 0
reward = 0
learning_rate = 0.5
doubling_cube_values = [1, 2, 4, 8, 16, 32, 64]

prob_of_rolling(5)
#print(prob_of_rolling(2))

# Testing
#cubeinfo = gnubg.cubeinfo()
#cube_owner = cubeinfo['doubled']
#pprint(cubeinfo)
#print(type(cubeinfo))

#s: turn until game ends
#a: double, don't double, accept double, reject double

while False:
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

    #cubeinfo = gnubg.match()
    #cube_owner = cubeinfo["match-info"]
    #pprint(cube_owner)

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

    # Commands an optimal move if a move is possible
    #players_turn = posinfo['turn']
    #if players_turn:
    gnubg.command('move ' + gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()), gnubg.board()))

    # Breaks the loop when a winner has been determined
    #if (str(determine_winner_1()) != 'None'):
    temp1, temp2 = determine_winner()
    if temp1 or temp2:
        print("Game Completed!")
        print(str(determine_winner_1()))
        break;

doubling_cube_value = find_doubling_cube_value()

if True:#player_wins_game:
    reward = 1 * (doubling_cube_value + 1000)
else:
    reward = -1 * (doubling_cube_value + 1000)

total_reward += reward
print(total_reward)
