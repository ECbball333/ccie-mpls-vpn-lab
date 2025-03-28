from netmiko import ConnectHandler
from getpass import getpass
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("USERNAME") or input("Username: ")
PASSWORD = os.getenv("PASSWORD") or getpass("Password: ")

VRF_CONFIGS = {
    "R1": {
        "host": "192.168.68.53",
        "commands": [
            "ip vrf BLUE",
            " no rd 1.1.1.1:10",
            " rd 1.1.1.1:10",
            " route-target export 65000:10",
            " route-target import 65000:10",
            "exit",
            "ip vrf RED",
            " no rd 1.1.1.1:20",
            " rd 1.1.1.1:20",
            " route-target export 65000:20",
            " route-target import 65000:20",
            "exit"
        ]
    },
    "R2": {
        "host": "192.168.68.54",
        "commands": [
            "ip vrf BLUE",
            " no rd 2.2.2.2:10",
            " rd 2.2.2.2:10",
            " route-target export 65000:10",
            " route-target import 65000:10",
            "exit",
            "ip vrf RED",
            " no rd 2.2.2.2:20",
            " rd 2.2.2.2:20",
            " route-target export 65000:20",
            " route-target import 65000:20",
            "exit"
        ]
    }
}

def configure_vrfs(name, host, commands):
    print(f"\nConnecting to {name} ({host})...")
    conn = ConnectHandler(
        device_type="cisco_ios",
        host=host,
        username=USERNAME,
        password=PASSWORD
    )
    print(f"Applying VRF config to {name} line by line...")
    conn.enable()
    conn.config_mode()
    for cmd in commands:
        try:
            output = conn.send_command_timing(cmd, strip_prompt=False, strip_command=False)
            print(f"{name}# {cmd}\n{output}")
        except Exception as e:
            print(f"[ERROR] {name} failed on command '{cmd}': {e}")
    conn.exit_config_mode()
    conn.disconnect()

if __name__ == "__main__":
    for name, device in VRF_CONFIGS.items():
        configure_vrfs(name, device["host"], device["commands"])

