import json
import os
import random
import bottle

import numpy as np
from scipy import signal

from api import ping_response, start_response, move_response, end_response

counter = 0
FRUITS_VALUE = 5
OTHER_SNAKE_VALUE = -5
MY_HEAD_VALUE = 0
CURRENT_HEAD_Y = 0
CURRENT_HEAD_X = 0
LAST_HEAD_Y = 0
LAST_HEAD_X = 0

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

def init(data):
    global CURRENT_HEAD_Y
    global CURRENT_HEAD_X

    w, h = data[u'board'][u'width'], data[u'board'][u'height']
    boardData = [[0 for x in range(w)] for y in range(h)]
    for fruits in data[u'board'][u'food']:
        boardData[fruits[u'y']][fruits[u'x']] = FRUITS_VALUE
    for snakes in data[u'board'][u'snakes']:
        if snakes[u'name'] in "ced":
            CURRENT_HEAD_Y = snakes[u'body'][0][u'y']
            CURRENT_HEAD_X = snakes[u'body'][0][u'x']
            boardData[CURRENT_HEAD_Y][CURRENT_HEAD_X] = MY_HEAD_VALUE
            continue
        for body_pieces in snakes[u'body']:
            boardData[body_pieces[u'y']][body_pieces[u'x']] = OTHER_SNAKE_VALUE

    return boardData

def applyfilterOnBoardData(boardData):
    npBoardData = np.array(boardData)

    sigma = 1.0  # width of kernel
    x = np.arange(-3, 4)  # coordinate arrays -- make sure they contain 0!
    y = np.arange(-3, 4)
    xx, yy = np.meshgrid(x, y)
    kernel = np.exp(-(xx ** 2 + yy ** 2) / (2 * sigma ** 2))

    filtered = signal.convolve(npBoardData, kernel, mode="same")
    filtered=filtered.astype(int)
    return filtered

def findFirstNeibord(boardData):
    currentMax = -900
    print(boardData[CURRENT_HEAD_Y][CURRENT_HEAD_X])
    neighborshood = neighbors(boardData,CURRENT_HEAD_Y,CURRENT_HEAD_X)
    return neighborshood


def neighbors(mat, row, col, radius=1):

    rows, cols = len(mat), len(mat[0])
    out = []

    for i in xrange(row - radius - 1, row + radius):
        row = []
        for j in xrange(col - radius - 1, col + radius):

            if 0 <= i < rows and 0 <= j < cols:
                row.append(mat[i][j])
            else:
                row.append(0)

        out.append(row)

    return out

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json


    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    #print(json.dumps(data))

    color = "#00FF00"

    return start_response(color)


def getPreferedDirection(neighborshood):
    #TOP
    top = np.array(neighborshood[0])
    topValue = np.mean(top)

    #LEFT
    npNH = np.array(neighborshood)
    left = np.array(npNH[:, 0])
    leftValue =  np.mean(left)

    #right
    right = np.array(npNH[:, npNH.shape[0]-1])
    rightValue =  np.mean(right)

    #bottom
    bottom = np.array(npNH[:, npNH.shape[1]-1])
    bottomValue =  np.mean(bottom)
    print("top:" + str(topValue) + "left:" + str(leftValue) + "right:" + str(rightValue) + "bottom:" + str(bottomValue))
    if topValue >= leftValue and topValue >= rightValue and topValue >= bottomValue :
        return 'up'
    elif leftValue >= topValue and leftValue >= rightValue and leftValue >= bottomValue :
        return 'left'
    elif rightValue >= topValue and rightValue >= leftValue and rightValue >= bottomValue :
        return 'right'
    else:
        return 'bottom'




@bottle.post('/move')
def move():
    data = bottle.request.json
    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
   # print(json.dumps(data))
    #json to simple 2D with default weight
    boardData = init(data)

    #2D array to gaussian weight
    boardData = applyfilterOnBoardData(boardData)

    #get the direction to the closest max
    neighborshood = findFirstNeibord(boardData)

    #get direction
    direction = getPreferedDirection(neighborshood)

    # global counter
    # counter += 1
    # if counter % 4 == 0:
    #     directions = ['up']
    # elif counter % 4 == 1:
    #     directions = ['left']
    # elif counter % 4 == 2:
    #     directions = ['down']
    # elif counter % 4 == 3:
    #     directions = ['right']


    return direction


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()


if __name__ == '__main__':
    c = 0
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
