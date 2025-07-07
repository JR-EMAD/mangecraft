import os, json, getpass

CONFIG_PATH = "config.json"

def load_or_setup_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    print("🔧 Welcome to Mangecraft setup")
    port = input("Enter port [8080]: ") or "8080"
    server_dir = input("Enter Minecraft server folder path: ").strip()
    username = input("Panel username: ")
    import getpass
    password = getpass.getpass("Panel password: ")

    config = {
        "port": int(port),
        "server_dir": server_dir,
        "username": username,
        "password": password
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    return config
