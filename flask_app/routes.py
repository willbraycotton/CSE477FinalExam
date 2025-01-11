# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database import database
from werkzeug.datastructures import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
import re
from . import socketio
from flask import send_from_directory, jsonify, render_template_string

db = database()
locked_cards = set()
#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
    return session['email'] if 'email' in session else 'Unknown'

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')



@app.route('/newboard')
@login_required
def board():
    return render_template('newboard.html')

@app.route('/logout')
def logout():
    session.pop('email', default=None)
    return redirect('/login')

@app.route('/processlogin', methods=["POST", "GET"])
def processlogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    check = db.authenticate(form_fields['email'], db.onewayEncrypt(form_fields['password']))
    if check['success'] == 1:
        session['email'] = form_fields['email']
        return json.dumps({'success': 1})
    else:
        return json.dumps({'success': 0})

# Board and Dashboard Management
@app.route('/dashboard')
@login_required
def dashboard():
    user_boards = db.get_user_boards(getUser())
    return render_template('dashboard.html', boards=user_boards, user=getUser())

@app.route('/create_board', methods=['POST'])
@login_required
def create_board():
    data = request.get_json()
    board_id = db.create_board(data['name'], data['members'], session['email'])
    if board_id:
        return jsonify({'board_id': board_id}), 201
    else:
        return jsonify({'board_id': 'Failed to create board'}), 500

#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser(), board_id=request.args.get('board_id'))

@socketio.on('joined', namespace='/chat')
def joined(data):
    board_id = data['board_id']
    join_room(board_id)
    if getUser() == 'owner@email.com':
        emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right;padding-top:7px'}, room=board_id)
    else:
        emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:grey;text-align: left;padding-top:7px'}, room=board_id)

@socketio.on('displaymessage', namespace='/chat')
def displaymessage(data):
    board_id = data['board_id']
    message = data['message']
    if getUser() == 'owner@email.com':
        emit('status', {'msg': message, 'style': 'width: 100%;color:blue;text-align: right'}, room=board_id)
    else:
        emit('status', {'msg': message, 'style': 'width: 100%;color:grey;text-align: left'}, room=board_id)

@socketio.on('leaveRoom', namespace='/chat')
def leaveRoom(data):
    board_id = data['board_id']
    leave_room(board_id)
    if getUser() == 'owner@email.com':
        emit('status', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room=board_id)
    else:
        emit('status', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:grey;text-align: left'}, room=board_id)

#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
    return redirect('/login')

@app.route('/home')
@login_required
def home():
    return render_template('home.html', user=getUser())

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/piano')
def piano():
    return render_template('piano.html')

@app.route('/resume')
def resume():
    resume_data = db.getResumeData()
    pprint(resume_data)
    return render_template('resume.html', resume_data=resume_data)

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    response.headers['Pragma'] = "no-cache"
    response.headers['Expires'] = "0"
    return response

@app.route('/register', methods=["POST", "GET"])
def register():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    check = db.createUser(form_fields['email'], form_fields['password'])
    if check['success'] == 1:
        session['email'] = form_fields['email']
        return json.dumps({'success': 1})
    else:
        return json.dumps({'success': 0})

#######################################################################################
# Board
#######################################################################################
@socketio.on('joined', namespace='/board')
def joinedboard(data):
    board_id = data['board_id']
    print('joined board')
    join_room(board_id)

@socketio.on('disconnect', namespace='/board')
def handle_disconnect():
    print(f'Client disconnected')


def can_access_board(board_id):
    user_email = session['email']
    user_results = db.query("SELECT user_id FROM users WHERE email = %s", (user_email,))
    user_id = user_results[0]['user_id'] if user_results else None

    if not user_id:
        return False

    access_results = db.query("""
        SELECT * FROM user_boards 
        WHERE user_id = %s AND board_id = %s
    """, (user_id, board_id))

    return bool(access_results)


@app.route('/board/<int:board_id>')
@login_required
def view_board(board_id):
    db = database()
    board = db.query("SELECT * FROM boards WHERE board_id = %s", (board_id,))
    cards = db.query("SELECT * FROM cards WHERE board_id = %s", (board_id,))
    
    
    if board and can_access_board(board_id):
        return render_template('board.html', board=board[0], cards=cards, user=getUser())
    else:
        return "Board not found", 404

@app.route('/user_boards')
@login_required
def user_boards():
    user_email = session['email']

    user_results = db.query("SELECT user_id FROM users WHERE email = %s", (user_email,))
    user_id = user_results[0]['user_id'] if user_results else None

    if not user_id:
        return jsonify({'error': 'User not found'}), 404

    boards = db.query("""
        SELECT b.board_id, b.name 
        FROM boards b
        INNER JOIN user_boards ub ON b.board_id = ub.board_id
        WHERE ub.user_id = %s
    """, (user_id,))

    return jsonify(boards)

@socketio.on('addcard', namespace='/board')
def add_card(data):
    card_name = data['name']
    list_name = data['list']
    board_id = data['board_id'] 
    success = db.query("INSERT INTO cards (name, list, board_id) VALUES (%s, %s, %s)", (card_name, list_name, board_id))
    card_id = success[0]["LAST_INSERT_ID()"]

    if list_name == 'To Do':
        list_name = 'todo'
    elif list_name == 'Doing':
        list_name = 'doing'
    elif list_name == 'Completed':
        list_name = 'completed'
    
    if success:
        
        card_html = render_template_string('''
        <input type="text" id="card-name-{{card_id}}" value="{{card_name}}" readonly>
            <div class="card-buttons">
                <button onclick="editCard('{{card_id}}')">Edit</button>
                <button onclick="saveCard('{{card_id}}')" style="display: none;">Save</button>
                <button onclick="deleteCard('{{card_id}}')">Delete</button>
            </div>
        ''', card_id=card_id, card_name=card_name)


        emit ('displayaddcard',{'card_html' : card_html, 'card_id': card_id, 'list': list_name}, room=board_id)
        return jsonify({'success': True, 'card_id': card_id})
    else:
        return jsonify({'error': 'Failed to add card'}), 500

@socketio.on('deletecard', namespace='/board')
def delete_card(data):
    card_id = data['card_id']
    board_id = db.query("SELECT board_id FROM cards WHERE card_id = %s", (card_id,))[0]['board_id']
    db.query("DELETE FROM cards WHERE card_id = %s", (card_id,))
    
    #join_room(board_id)
    emit('displaydeletecard', {'card_id': card_id}, broadcast=True)

    return jsonify({'success': True})

@socketio.on('updatecard', namespace='/board')
def update_card(data):
    print('update card')
    card_name = data['card_name']
    card_id = data['card_id']
    board_id = data['board_id']
    list = data['list']
    db.query("UPDATE cards SET name = %s WHERE card_id = %s", (card_name, card_id))
    
    card_html = render_template_string('''
        <input type="text" id="card-name-{{card_id}}" value="{{card_name}}" readonly>
            <div class="card-buttons">
                <button onclick="editCard('{{card_id}}')">Edit</button>
                <button onclick="saveCard('{{card_id}}')" style="display: none;">Save</button>
                <button onclick="deleteCard('{{card_id}}')">Delete</button>
            </div>
        ''', card_id=card_id, card_name=card_name)
    
    emit('displaydeletecard', {'card_id': card_id}, room=board_id)
    emit ('displayaddcard',{'card_id': card_id, 'name': card_name, 'list': list, 'card_html': card_html}, room=board_id)
    return

@socketio.on('updatecardlist', namespace='/board')
def update_card_list(data):

    new_list = data['new_list']
    card_id = data['card_id']
    board_id = data['board_id']
    card_name = data['card_name']

    if new_list == 'todo':
        new_list_proper = 'To Do'
    elif new_list == 'doing':
        new_list_proper = 'Doing'
    elif new_list == 'completed':
        new_list_proper = 'Completed'

    db.query("UPDATE cards SET list = %s WHERE card_id = %s", (new_list_proper, card_id))

    card_html = render_template_string('''
        <input type="text" id="card-name-{{card_id}}" value="{{card_name}}" readonly>
            <div class="card-buttons">
                <button onclick="editCard('{{card_id}}')">Edit</button>
                <button onclick="saveCard('{{card_id}}')" style="display: none;">Save</button>
                <button onclick="deleteCard('{{card_id}}')">Delete</button>
            </div>
        ''', card_id=card_id, card_name=card_name)
    
    emit('displaydeletecard', {'card_id': card_id}, room=board_id)
    emit ('displayaddcard',{'card_id': card_id, 'name': card_name, 'list': new_list, 'card_html': card_html}, room=board_id)
    return jsonify({'status': 'success'})

@socketio.on('lockcard', namespace='/board')
def lock_card(data):
    card_id = data['card_id']
    board_id = data['board_id']
    if card_id in locked_cards:
        print('card already locked')
        return {'status': 'failed'}
    
    locked_cards.add(card_id)
    print('emitting card locked')
    print('board Id:', board_id)
    emit('cardlocked', {'card_id': card_id}, broadcast = True, room=board_id)
    return {'status': 'sucess', 'card_id': card_id}



@socketio.on('unlockcard', namespace='/board')
def unlock_card(data):
    card_id = data['card_id']
    #board_id = data['board_id'
    locked_cards.remove(card_id)
    print('unLock car in routes')
    emit('cardunlocked', {'card_id': card_id}, broadcast=True)



@app.route('/card-template')
def card_template():
    return render_template('card-template.html')





