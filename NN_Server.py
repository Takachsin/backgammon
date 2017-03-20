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
# *********************************************

def calc_reward(pPip, oPip, cubeValue):
    if pPip > oPip:
        r = cubeValue
    elif pPip < oPip:
        r = -1 * cubeValue
    else:
        r = 0
    return r

def update_Q(pPip, oPip, pBar, oBar, a, r):
    Q = Q[pPip, oPip, pBar, oBar, a] + lr * (r + y *np.max(Q[pPip, oPip, pBar, oBar, :]) - Q[pPip, oPip, pBar, oBar, a])
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

            # Pull information out of received dictionary
            pPip = inputs['player_pip']
            oPip = inputs['opponent_pip']
            pBar = inputs['player_bar_count']
            oBar = inputs['opponent_bar_count']
            a = inputs['doubled']
            cubeValue = inputs['cube_value']

            r = calc_reward(pPip, oPip, cubeValue)
            r = calc_reward(pPip, oPip, cubeValue)

            Q = np.zeros([pip_max, pip_max, num_bar, num_bar, num_actions])
            #Q = np.zeros([pip_max, pip_max, num_bar, num_bar, num_actions])
            #Q[s, a] = Q[s,a] + learning_rate * (reward + discount_factor * np.max(Q[s1,:]) - Q[s,a])

            Q[pPip, oPip, pBar, oBar, a] = r
            Q[pPip, oPip, pBar, oBar, a] = Q[pPip, oPip, pBar, oBar, a] + lr * (r + y *np.max(Q[pPip, oPip, pBar, oBar, :]) - Q[pPip, oPip, pBar, oBar, a])
            print(Q[pPip, oPip, pBar, oBar, a])

            rs = {'RsSuccess': True, 'Payload': 1}
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


         #reward = calc_reward(pPip, oPip, doubling_cubeValue)



        # Example response



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
