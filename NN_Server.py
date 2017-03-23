import tensorflow as tf
import socket
import json
import numpy as np
import matplotlib.pyplot as plt

# vvv - Socket Magic -------------
TCP_IP = '127.0.0.1'
TCP_PORT = 50005
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
# ^^^ - Socket Magic -------------

# ************Set Parameters*******************
lr = 0.85 # learning rate
y = 0.99 # discount factor
pip_max = 375
num_bar = 3
num_actions = 2
# Initial values
Q = []
pPip = 167
oPip = 167
board = [-2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, -5, 5, 0, 0, 0 -3, 0, -5, 0, 0, 0, 0, 0]
pBar = 0
oBar = 0
pDoubled = 0 # no one has doubled
canDouble = 2 # either player can double

# Create initial state list
st = board
st.append(pBar)
st.append(oBar)
st.append(pDoubled)
st.append(canDouble)
# *********************************************

def calc_reward(pPip, oPip, cube):
    if pPip > oPip:
        r = cube
    elif pPip < oPip:
        r = -1 * cube
    else:
        r = 0
    return r

def update_Q(pPip, oPip, a, r):
    Q = Q[pPip, oPip, a] + lr * (r + y *np.max(Q[pPip, oPip, :]) - Q[pPip, oPip, a])
    return

# Run the Loop. This is a server so we will just kill it violently if needed
while 1:
    try:
        # Accept any requesting connection
        conn, addr = s.accept()
        print('Connection address:', addr)

        # Receive the incoming request
        request = conn.recv(BUFFER_SIZE)

        # If the incoming request isn't null, convert it to our Dict
        if request != None:
            inputs = json.loads(request.decode())
            print("I received: ", inputs)

            # Decide whether or not to take the action
            #Qindex0 = Q.index([st, 0])
            #Qindex1 = Q.index([st, 1])
            #if Q[Qindex1] > Q[Qindex0]:
            a = 1
            rs = {'RsSuccess': True, 'Payload': 1}
            #else:
            #    a = 0
            #    rs = {'RsSuccess': True, 'Payload': 0}

            # Pull information out of received dictionary
            nBoard = inputs['board']
            npPip = inputs['player_pip']
            noPip = inputs['opponent_pip']
            npBar = inputs['player_bar_count']
            noBar = inputs['opponent_bar_count']
            #a = inputs['doubled']
            cube = inputs['cube_value']
            cOwner = inputs['cube_owner']
            npDoubled = inputs['pDoubled']

            # canDouble = 0 for opponent, 1 for player, 2 for both
            if cOwner == 1:
                nCanDouble = 1
            elif cOwner == 0:
                nCanDouble = 0
            else:
                nCanDouble = 2

            # Create state list
            nSt = nBoard
            nSt.append(npBar)
            nSt.append(noBar)
            nSt.append(npDoubled)
            nSt.append(nCanDouble)

            # Add the state, action index to the Q table if it does not exist
            if not [st, a] in Q:
                Q.append([st, a])
                print("Appended")
            Qindex = Q.index([st, a])

            r = calc_reward(pPip, oPip, cube)
            Q[Qindex] = r
            print(Q[Qindex])

            #Q[pPip, oPip, a] = r
            #Q[ipPip, ioPip, ipBar, ioBar, a] = Q[ipPip, ioPip, ipBar, ioBar, a] + lr * (r + y *np.max(Q[pPip, oPip, pBar, oBar, :]) - Q[ipPip, ioPip, ipBar, ioBar, a])
            #print(Q[pPip, oPip, pBar, oBar, a])

            pPip = npPip
            oPip = noPip
            st = nSt

        else:
            rs = {'RsSuccess': False}

        # "Inputs" in this case, is your raw request object. You may either send
        # exactly what the server needs or format your request a bit. I would suggest
        # sending a dictionary that contains a string (train || query) and then the
        # payload of a Dict with all your inputs. Run this request through the NN
        # and then formulate a response based on your NN's findings.

        # action are double or don't double
        # states are iterations
        '''States can be the two pip counts plus which entries on the bar have
         two or more, exactly one, or zero of each color.
         That should reduce the state space somewhat but still capture key info.'''

        # Convert our response to a json string
        strResponse = json.dumps(rs)

        # Convert our response to Bytes
        response = strResponse.encode()

        # Publish the response and close the connection, then start over
        conn.send(response)  # Response
        conn.close()
    except Exception as ex:
        print(ex)


#toString
#s=json.dumps(variables)

#toDict
#variables2=json.loads(s)

##import tensorflow as tf
#hello = tf.constant('Hello, TensorFlow!')
#sess = tf.Session()
#print(sess.run(hello))

#x = tf.placeholder(tf.float32, [None, 784])
#W = tf.Variable(tf.zeros([784, 10]))
#b = tf.Variable(tf.zeros([10]))

#y = tf.nn.softmax(tf.matmul(x, W) + b)
