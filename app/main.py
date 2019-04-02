import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

counter = 0
FRUITS_VALUE = 1
OTHER_SNAKE_VALUE = -1
@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

def init(data):
    w, h = data[u'board'][u'width'],data[u'board'][u'height']
    boardData = [[0 for x in range(w)] for y in range(h)]
    for fruits in data[u'board'][u'food']:
        boardData[fruits[u'y']][fruits[u'x']] = FRUITS_VALUE
    for snakes in data[u'board'][u'snakes']:
        for body_pieces in snakes[u'body']:
            boardData[body_pieces[u'y']][body_pieces[u'x']] = OTHER_SNAKE_VALUE
    return data

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

@bottle.post('/move')
def move():
    data = bottle.request.json
    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))
    grid = init(data)
    global counter
    counter += 1
    if counter % 4 == 0:
        directions = ['up']
    elif counter % 4 == 1:
        directions = ['left']
    elif counter % 4 == 2:
        directions = ['down']
    elif counter % 4 == 3:
        directions = ['right']

    direction = random.choice(directions)

    return move_response(direction)


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
