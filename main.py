from flask import Flask, render_template, request, redirect, session, Response, jsonify
import os
import config
import server_control as sc

app = Flask(__name__)
app.secret_key = os.urandom(24)
config.config = config.load_or_setup_config()  # Load once, assign globally

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == config.config['username'] and request.form['password'] == config.config['password']:
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
    status = "Online" if sc.is_online() else "Offline"
    players = sc.get_players()
    return render_template('panel.html', status=status, players=players)

@app.route('/start_server')
def route_start_server():
    if not session.get('logged_in'):
        return redirect('/')
    sc.start_server()
    return redirect('/panel')

@app.route('/stop_server')
def route_stop_server():
    if not session.get('logged_in'):
        return redirect('/')
    sc.stop_server()
    return redirect('/panel')

@app.route('/send_command', methods=['POST'])
def route_send_command():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    cmd = request.form.get('command', '')
    sc.send_command(cmd)
    return '', 204

@app.route('/kick_player', methods=['POST'])
def kick_player():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    player = request.form.get('player')
    sc.send_command(f"kick {player}")
    return jsonify(success=True)

@app.route('/ban_player', methods=['POST'])
def ban_player():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    player = request.form.get('player')
    sc.send_command(f"ban {player}")
    return jsonify(success=True)

@app.route('/logs')
def logs():
    def event_stream():
        yield from sc.get_logs()
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/players')
def players_api():
    if not session.get('logged_in'):
        return jsonify([])
    return jsonify(sc.get_players())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.config['port'])
