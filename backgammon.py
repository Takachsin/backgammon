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
    return response['Payload']

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
epochs = 100
matchto = 7
verbose = True
# *********************************************

# Calculate the number of spaces remaining to bear off all checkers
def calc_pip_count():
    pPip = 0
    oPip = 0
    board = gnubg.board()
    oBoard, pBoard = board
    for x in range (0,24):
        pPip = pPip + pBoard[x] * (x+1)
    for x in range (0,24):
        oPip = oPip + oBoard[x] * (x+1)
    return pPip, oPip

# Finds a restricted count of how many checkers each player has on the bar
def calc_checkers_on_bar():
    board = gnubg.board()
    oBoard, pBoard = board
    pBarCount = pBoard[24]
    oBarCount = oBoard[24]
    if pBarCount >= 2:
        pBar = 2
    else:
        pBar = pBarCount

    if oBarCount >= 2:
        oBar = 2
    else:
        oBar = oBarCount
    return pBar, oBar

# Creates a single array to show checker positions on the board
# Player checkers are positive and opponent checkers are negative
def calc_board_diff():
    board = gnubg.board()
    pBoard = list(board[1][0:24])
    oBoard = list(board[0][0:24])
    pBar = board[1][24]
    oBar = board[0][24]
    dBoard = pBoard
    for x in range(len(pBoard)):
        dBoard[x] = pBoard[x] - oBoard[23 - x]
    return dBoard, pBar, oBar

# Determines if a player is bearing off based on the chip positions
def determine_if_game_has_ended():
    board = gnubg.board()
    oBoard, pBoard = board
    pWins = all(item == 0 for item in pBoard)
    oWins = all(item == 0 for item in oBoard)
    return pWins, oWins

# Determines if a player is bearing off based on the chip positions
def determine_bearing_off():
    board = gnubg.board()
    oBoard, pBoard = board

    # uses [6:] to skip checking the checkers in the bearing off zone
    pBearOff = all(item == 0 for item in pBoard[6:])
    oBearOff = all(item == 0 for item in oBoard[6:])
    return pBearOff, oBearOff

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

def build_NNdict():
    evaluate = gnubg.evaluate()
    pPip, oPip = calc_pip_count()
    board, pBar, oBar = calc_board_diff()

    # Build dictionary to send to the NN server
    NNdict['board'] = board
    NNdict['player_pip'] = pPip
    NNdict['opponent_pip'] = oPip
    NNdict['player_bar_count'] = pBar
    NNdict['opponent_bar_count'] = oBar
    NNdict['cube_value'] = cubeinfo['cube']
    NNdict['cube_owner'] = cubeinfo['cubeowner']
    NNdict['player_wins_prob'] = evaluate[0]
    return

gnubg.command('set automatic game off')
matches_won = 0

for x in xrange(0, epochs):
    # Start the game
    if verbose: print("Starting Game " + str(x))
    gnubg.command('new match ' + str(matchto))

    # initialize values
    pWins = False
    oWins = False
    NNdict = {}
    NNdict['game_over'] = False
    NNdict['player_wins'] = False
    NNdict['epochs'] = epochs
    NNdict['current_epochs'] = x

    while not pWins and not oWins:
        try:
            # Breaks the loop when a winner has been determined
            pWins, oWins = determine_if_game_has_ended()
            if pWins or oWins:
                if verbose: print("Game Completed, woohoo!")
                break

            posinfo = gnubg.posinfo()
            cubeinfo = gnubg.cubeinfo()
            match = gnubg.match()

            opponent_doubled = posinfo['doubled']
            opponent_resigns = posinfo['resigned']
            opponent_has_cube = cubeinfo['cubeowner'] == 0
            die1, die2 = posinfo['dice']
            double = False

            # Decides whether to accept the oppoent's double
            if opponent_doubled:
                NNdict['double'] = 2
                build_NNdict()
                accept = Query_NN(NNdict)
                if accept:
                    if verbose: print("Player accepts double.")
                    gnubg.command('accept')
                else:
                    if verbose: print("Player rejects double, and loses match.")
                    pWins = False
                    oWins = True
                    gnubg.command('reject')
                    break
            # Accepts the resignation when the opponent offers to resign
            elif opponent_resigns:
                if verbose: print("Opponent resigns!")
                pWins = True
                oWins = False
                gnubg.command('accept')
                break
            # Checks to make sure the player has not rolled yet
            elif die1 == 0 and die2 == 0:
                if not opponent_has_cube:
                    # Decides whether player should double before rolling
                    NNdict['double'] = 1
                    build_NNdict()
                    double = Query_NN(NNdict)
                    print(double)
                    if double:
                        gnubg.command('double')
                gnubg.command('roll')
            else:
                gnubg.command('move ' + gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()), gnubg.board()))
                #gnubg.command(gnubg.movetupletostring(gnubg.findbestmove(gnubg.board(), gnubg.cubeinfo()),gnubg.board()))

            NNdict['double'] = 0
            build_NNdict()
            Query_NN(NNdict)
        except Exception as ex:
            print(ex)
            gnubg.updateui()
            gnubg.command("accept")
            if gnubg.match()['games'][-1]['info']['resigned'] == True:
                if verbose: print("Opponent resigns!")
                pWins = True
                oWins = False
                gnubg.command('accept')

    if pWins:
        if verbose: print("Player has won the game!")
        matches_won += 1
    else:
        if verbose: print("Opponent has won the game!")

    build_NNdict()
    NNdict['game_over'] = True
    NNdict['player_wins'] = pWins
    Query_NN(NNdict)

print("Player won " + str(matches_won) + " of " + str(epochs) + " matches")
