
from random import randint
import sched, time

from flask import Flask
# from flask_cors import CORS
from flask_socketio import SocketIO, emit






app = Flask('meg.fm')
# CORS(app)

socketio = SocketIO(app, cors_allowed_origins='*')


@socketio.on('connect')
def handle_connect():
    print('user connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('user disconnected')


scheduler = sched.scheduler(time.time, time.sleep)
def change_title(sc):
    print('emitting changetitle')
    socketio.emit('changetitle', randint(0, 9999))
    sc.enter(5, 1, change_title, (sc,))
# scheduler.enter(0, 1, change_title, (scheduler,))

def start_scheduler():
    # change_title(scheduler)
    scheduler.enter(1, 1, change_title, (scheduler,))
    scheduler.run()



# if __name__ == '__main__':
socketio.start_background_task(start_scheduler)
socketio.run(app)
