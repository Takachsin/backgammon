from pprint import pprint
import socket
import json
import time

# Setup to transfer data between the backgammon client and python server
# Credit to Ben Smith
def Train_NN(xs, ys):
    "Train the NN"
    return

def Query_NN(xs):
    "Call the NN to determine an action"
    response = Client_Send(xs)
    return response['RsSuccess']

def Client_Send(data):
    "Send Data to NN Server"
    TCP_IP = '127.0.0.1'
    TCP_PORT = 50005
    BUFFER_SIZE = 1024
    try:
        # Convert the Dictionary "Data" into a string
        strRequest = json.dumps(data)

        # Convert the json string into Bytes
        request = strRequest.encode()
        try:
            # Connect to the Socket and send the request
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            s.send(request)

            # Wait for the response from the Server
            rs = s.recv(BUFFER_SIZE)
        finally:
            s.close()

        # if the response isn't null, write it out and return the dictionary
        # form of the response
        if rs != None:
            strResponse = rs.decode()
            print("I received: " + strResponse)
            response = json.loads(strResponse)
            return response
    except Exception as ex:
        print(ex)

# ************Set Parameters*******************
learning_rate = 0.85
discount_factor = 0.99
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

# Finds a restricted count of how many checkers each player has on the bar
def calc_checkers_on_bar():
    board = gnubg.board()
    opponent_board, player_board = board
    player_checkers_on_bar = player_board[24]
    opponent_checkers_on_bar = opponent_board[24]

    if player_checkers_on_bar >= 2:
        player_bar_count = 2
    else:
        player_bar_count = player_checkers_on_bar

    if opponent_checkers_on_bar >= 2:
        opponent_bar_count = 2
    else:
        opponent_bar_count = opponent_checkers_on_bar

    return player_bar_count, opponent_bar_count

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

matches_won = 0

for x in xrange(0, epochs):
    # Start the game
    if verbose: print("Starting Game " + str(x))
    gnubg.command('new match ' + str(matchto))

    # initialize values
    total_reward = 0
    player_has_won = False
    opponent_has_won = False
    NN_dict = {}

    while not player_has_won and not opponent_has_won:
        # Breaks the loop when a winner has been determined
        player_has_won, opponent_has_won = determine_if_game_has_ended()
        if player_has_won or opponent_has_won:
            if verbose: print("Game Completed, woohoo!")
            break

        posinfo = gnubg.posinfo()
        cubeinfo = gnubg.cubeinfo()
        board = gnubg.board()
        match = gnubg.match()

        #player_score = match['games'][-1]['info']['score-O']
        #opponent_score = match['games'][-1]['info']['score-X']
        opponent_doubled = posinfo['doubled']
        opponent_resigns = posinfo['resigned']
        opponent_has_cube = cubeinfo['cubeowner'] == 0
        die_1, die_2 = posinfo['dice']

        # Decides whether to accept the oppoent's double
        if opponent_doubled:
            double = decide_on_double()
            if double:
                if verbose: print("Player accepts double.")
                gnubg.command('accept')
            else:
                if verbose: print("Player rejects double, and loses match.")
                player_has_won = False
                opponent_has_won = True
                gnubg.command('reject')
                break
        # Accepts the resignation when the opponent offers to resign
        elif opponent_resigns:
            if verbose: print("Opponent resigns!")
            player_has_won = True
            opponent_has_won = False
            gnubg.command('accept')
            break
        # Checks to make sure the player has not rolled yet
        elif die_1 == 0 and die_2 == 0:
            # Decides whether player should double before rolling
            if not opponent_has_cube:
                double = decide_on_double()
                if double:
                    gnubg.command('double')
            gnubg.command('roll')
        else:
            gnubg.command('move ' + gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()), gnubg.board()))
            #gnubg.command(gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()),gnubg.board()))

        player_pip, opponent_pip = calc_pip_count()
        player_bar_count, opponent_bar_count = calc_checkers_on_bar()
        NN_dict['player_pip'] = player_pip
        NN_dict['opponent_pip'] = opponent_pip
        NN_dict['player_bar_count'] = player_bar_count
        NN_dict['opponent_bar_count'] = opponent_bar_count
        NN_dict['doubling_cube_value'] = cubeinfo['cube']
        Query_NN(NN_dict)

    if player_has_won:
        if verbose: print("Player has won the game!")
        matches_won += 1
        #reward = 1 * (doubling_cube_value + 1000)
    else:
        if verbose: print("Opponent has won the game!")
        #reward = -1 * (doubling_cube_value + 1000)

print("Player won " + str(matches_won) + " of " + str(epochs) + " matches")
