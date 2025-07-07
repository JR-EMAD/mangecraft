import os
import json
import getpass

CONFIG_PATH = "config.json"

def load_or_setup_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    print("🔧 Welcome to Mangecraft setup")
    port = input("Enter panel port [8080]: ") or "8080"
    server_dir = input("Enter Minecraft server folder path: ").strip()
    server_jar = input("Enter server JAR filename (e.g. server.jar): ").strip()
    username = input("Panel username: ")
    password = getpass.getpass("Panel password: ")
    server_ip = input("Minecraft server IP [127.0.0.1]: ") or "127.0.0.1"
    rcon_port = input("RCON port [25575]: ") or "25575"
    rcon_password = getpass.getpass("RCON password: ")

    config = {
        "port": int(port),
        "server_dir": server_dir,
        "server_jar": server_jar,
        "username": username,
        "password": password,
        "server_ip": server_ip,
        "rcon_port": int(rcon_port),
        "rcon_password": rcon_password
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    return config
