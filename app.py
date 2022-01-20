from flask import Flask, render_template, request
from flask_socketio import SocketIO
import csv
from random import randrange 

app = Flask(__name__)
socketio = SocketIO(app)

rows = []
total_list = []
"""
The CSV is in the following format:

Opening name, link to opening, opening moves
"""
@app.before_first_request
def loadCSVData():
    with open('openings.csv', 'r', errors='ignore') as csvfile:
        csvreader = csv.reader(csvfile) 
        for row in csvreader: 
            rows.append(row)

    for row in rows:

        # since the CSV has the opening moves
        # stored as space separated like this:
        # 1.e4 Nf6 2.e5 Nd5 3.d4 d6 4.Nf3 g6,
        # we have to parse the moves into a proper format

        movesTemp = (row[2]).split()
        newMovesTemp = []
        for move in movesTemp:
            if "." in move:
                move = move.split('.')[1]

            newMovesTemp.append(move)

        total_list.append([row[0], row[1], newMovesTemp])

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('opponent_move')
def opponent_move(game):
    socketID = request.sid
    returnDict = getRandomMove(game['curGame'])
    if returnDict == None:
        socketio.emit('done', room=socketID)
    else:
        socketio.emit('yourMove', returnDict, room=socketID)

def getRandomMove(movesList):

    #if it is a first move
    if movesList == []:
        randEntry = randrange(len(total_list))
        move = total_list[randEntry][2][0]
        dict = {'name':total_list[randEntry][0], 'link':total_list[randEntry][1], 'move':move}
        return dict

    else:
        posOptions = []
        #looping through all options in our master list
        for op in total_list:
            opMoves = op[2]
            #looping through all already submitted moves
            if len(opMoves) > len(movesList):
                for i in range(len(movesList)):
                    if opMoves[i] == movesList[i]:
                        #if it matches and it's the last one in the list, we can use it
                        if i == (len(movesList) - 1):
                            posOptions.append(op)
                    #if they don't match, we break
                    else:
                        break

        if posOptions == []:
            return None
        else:
            randEntry = randrange(len(posOptions))
            move = posOptions[randEntry][2][len(movesList)]
            dict = {'name':posOptions[randEntry][0], 'link':posOptions[randEntry][1], 'move':move}
            return dict

if __name__ == "__main__":
    app.run()