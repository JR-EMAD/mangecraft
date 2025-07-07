from flask import Flask, render_template, request, redirect, session, Response, jsonify
import os
from config import load_or_setup_config
from server_control import start_server, stop_server, send_command, get_logs, get_players, is_online

app = Flask(__name__)
app.secret_key = os.urandom(24)
config = load_or_setup_config()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == config['username'] and request.form['password'] == config['password']:
            session['logged_in'] = True
            return redirect('/panel')
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/panel')
def panel():
    if not session.get('logged_in'):
        return redirect('/')
    status = "Online" if is_online() else "Offline"
    players = get_players()
    return render_template('panel.html', status=status, players=players)

@app.route('/start_server')
def route_start_server():
    if not session.get('logged_in'):
        return redirect('/')
    start_server(config['server_dir'])
    return redirect('/panel')

@app.route('/stop_server')
def route_stop_server():
    if not session.get('logged_in'):
        return redirect('/')
    stop_server()
    return redirect('/panel')

@app.route('/send_command', methods=['POST'])
def route_send_command():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    cmd = request.form.get('command', '')
    send_command(cmd)
    return '', 204

@app.route('/kick_player', methods=['POST'])
def kick_player():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    player = request.form.get('player')
    send_command(f"kick {player}")
    return jsonify(success=True)

@app.route('/ban_player', methods=['POST'])
def ban_player():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    player = request.form.get('player')
    send_command(f"ban {player}")
    return jsonify(success=True)

@app.route('/logs')
def logs():
    def stream():
        yield from get_logs()
    return Response(stream(), mimetype="text/event-stream")

@app.route('/players')
def players_api():
    if not session.get('logged_in'):
        return jsonify([])
    return jsonify(get_players())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config['port'])
