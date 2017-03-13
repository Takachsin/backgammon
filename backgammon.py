from pprint import pprint

# Pulls the doubling cube information from GNUBG
def find_doubling_cube_value():
    cubeinfo = gnubg.cubeinfo()
    doubling_cube_value = cubeinfo["cube"]
    return doubling_cube_value;

# Calculate the number of spaces remaining to bear off all checkers
def calculate_pip_count():
    player_pip = 0
    opponent_pip = 0
    board = gnubg.board()
    opponent_board, player_board = board
    for x in xrange (0,24):
        player_pip = player_pip + player_board[x] * (x+1)
    for x in xrange (0,24):
        opponent_pip = opponent_pip + opponent_board[x] * (x+1)
    return player_pip, opponent_pip;

def determine_winner():
    board = gnubg.board()
    opponent_board, player_board = board
    temp1 = all(player_board == 0 for item in board)
    temp2 = all(opponent_board == 0 for item in board)
    print(temp1)
    print(temp2)
    return temp1, temp2;

def determine_winner_1():
    match = gnubg.match()
    match_info = match["games"]
    return match_info[0]['info']['winner'];

def decide_on_cube():
    player_pip, opponent_pip = calculate_pip_count()
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
    return double, reward;

# Defines the probability off winning
def probability():
    return;

# Start the game
print("Starting Game")
gnubg.command('new game')
#gnubg.command('show pipcount')
total_reward = 0
reward = 0

# Testing
cubeinfo = gnubg.cubeinfo()
#cube_owner = cubeinfo['doubled']
pprint(cubeinfo)
#print(type(cubeinfo))

while True:
    posinfo = gnubg.posinfo()
    cubeinfo = gnubg.cubeinfo()

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
        double, reward = decide_on_cube()
        if double:
            print("Player accepts double.")
            gnubg.command('accept')
        else:
            print("Player rejects double, and loses match.")
            player_wins_game = False
            gnubg.command('reject')
            break;
        total_reward += reward

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
    double, reward = decide_on_cube()
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
    reward = 1000 * doubling_cube_value
else:
    reward = -1000 * doubling_cube_value

total_reward += reward
print(total_reward)
