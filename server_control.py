import subprocess
import threading
from queue import Queue
import time
import re

mc_process = None
log_queue = Queue()
players = set()

def start_server(server_dir):
    global mc_process
    if mc_process is None or mc_process.poll() is not None:
        mc_process = subprocess.Popen(
            ["java", "-Xmx1G", "-jar", "server.jar", "nogui"],
            cwd=server_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        threading.Thread(target=read_output, daemon=True).start()
        threading.Thread(target=periodic_player_list, daemon=True).start()

def stop_server():
    global mc_process
    if mc_process and mc_process.poll() is None:
        mc_process.stdin.write("stop\n")
        mc_process.stdin.flush()

def send_command(cmd):
    if mc_process and mc_process.poll() is None:
        mc_process.stdin.write(cmd + "\n")
        mc_process.stdin.flush()

def read_output():
    global players
    player_pattern = re.compile(r'\[Server thread/INFO\]: Players online: \((\d+)\) \[(.*?)\]')
    player_list_pattern = re.compile(r'\[Server thread/INFO\]: (?:PlayerList|Connected players): (.*)')  # just in case
    while True:
        line = mc_process.stdout.readline()
        if not line:
            break
        line = line.strip()
        log_queue.put(line)

        # Try to parse player list from output when 'list' command result comes
        if "There are" in line and "players online:" in line:
            # example: [Server thread/INFO]: There are 1 of a max 20 players online: JR_EMAD
            parts = line.split(": ")
            if len(parts) >= 2:
                plist = parts[-1].strip()
                if plist.lower() == "no players online":
                    players = set()
                else:
                    players = set(p.strip() for p in plist.split(","))
        # Another possible pattern (for other versions)
        elif player_pattern.search(line):
            match = player_pattern.search(line)
            plist_raw = match.group(2)
            players = set(p.strip() for p in plist_raw.split(",") if p.strip())

def periodic_player_list():
    while True:
        if mc_process and mc_process.poll() is None:
            send_command("list")
        time.sleep(10)  # هر 10 ثانیه لیست پلیرها رو آپدیت کن

def get_logs():
    while True:
        line = log_queue.get()
        yield f"data: {line}\n\n"

def get_players():
    return list(players)

def is_online():
    return mc_process and mc_process.poll() is None
