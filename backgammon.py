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
reward = 0 # reward for current game

# Testing
#cubeinfo = gnubg.positionkey()
#cube_owner = cubeinfo["analysis"]
#pprint(cubeinfo)

# Monitor player board layout
#past_player_board = [0] * 25
#board = gnubg.board()
#opponent_board, player_board = board
#temp1 = all(player_board == 0 for item in board)
#temp2 = all(player_board == 0 for item in board)
#if (player_board != past_player_board):
#    print("not equal")

while True:
    # Breaks the loop when a winner has been determined
    if (str(determine_winner()) != "None"):
        print("Game Completed!")
        break;

    # Decides whether to accept the oppoent's double
    '''
    if opponent doubles:
        double, reward = decide_on_cube()
        if double:
            gnubg.command('accept')
        else:
            gnubg.command('reject')
    '''

    # Accepts the resignation when the opponent offers to resign
    '''
    if opponent resigns:
        gnubg.command('accept')
    '''

    # Cubeowner = 1 if opponent, -1 if no one, 0 if player
    #cube_in_control = cube owner -1 or 0

    # Decides whether player should double before rolling
    '''
    double, reward = decide_on_cube()
    #if double and cube_in_control:
        #gnubg.command('double')
    '''

    gnubg.command('roll')

    # Commands the best move if a move is possible
    #if can_move
    gnubg.command('move ' + gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()), gnubg.board()))

# temporary value, will be determined if player wins
win_game = True
doubling_cube_value = find_doubling_cube_value()

if win_game:
    reward = 1 * (doubling_cube_value + 1000)
else:
    reward = -1 * (doubling_cube_value + 1000)

#print(reward)
