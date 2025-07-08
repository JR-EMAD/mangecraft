import re
from mcrcon import MCRcon
import subprocess
import threading
import time
import config

mc_process = None
mc_process_lock = threading.Lock()
log_lines = []
log_lock = threading.Lock()

def clean_minecraft_colors(text):
    return re.sub(r'§.', '', text)

def start_server():
    global mc_process
    with mc_process_lock:
        if mc_process is None or mc_process.poll() is not None:
            mc_process = subprocess.Popen(
                ["java", "-Xmx1G", "-jar", config.config["server_jar"], "nogui"],
                cwd=config.config["server_dir"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            threading.Thread(target=read_output, daemon=True).start()

def stop_server():
    send_command("stop")

def send_command(cmd):
    try:
        with MCRcon(config.config["server_ip"], config.config["rcon_password"], port=config.config["rcon_port"]) as mcr:
            response = mcr.command(cmd)
            if response:
                with log_lock:
                    log_lines.append(f"> {cmd}")
                    for line in response.strip().splitlines():
                        log_lines.append(line)
    except Exception as e:
        with log_lock:
            log_lines.append(f"[RCON ERROR] {str(e)}")

def get_players():
    try:
        with MCRcon(config.config["server_ip"], config.config["rcon_password"], port=config.config["rcon_port"]) as mcr:
            response = mcr.command("list")
            response = clean_minecraft_colors(response)

            if "players online" in response:
                if ":" in response:
                    players_part = response.split(":")[-1].strip()
                    if players_part.lower() == "no players online" or players_part == "":
                        return []
                    return [p.strip() for p in players_part.split(",")]
    except Exception as e:
        with log_lock:
            log_lines.append(f"[RCON ERROR] {str(e)}")
    return []

def is_online():
    try:
        with MCRcon(config.config["server_ip"], config.config["rcon_password"], port=config.config["rcon_port"]) as mcr:
            mcr.command("list")
        return True
    except:
        return False

def read_output():
    global mc_process
    while mc_process and mc_process.poll() is None:
        line = mc_process.stdout.readline()
        if line:
            with log_lock:
                log_lines.append(line.strip())
        else:
            time.sleep(0.1)

def get_logs():
    last_index = 0
    while True:
        with log_lock:
            new_logs = log_lines[last_index:]
            last_index = len(log_lines)
        for line in new_logs:
            yield f"data: {line}\n\n"
        time.sleep(1)
