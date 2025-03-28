from netmiko import ConnectHandler
from getpass import getpass
from dotenv import load_dotenv
import os
import time

load_dotenv()

USERNAME = os.getenv("USERNAME") or input("Username: ")
PASSWORD = os.getenv("PASSWORD") or getpass("Password: ")

DEVICES = {
    "R1": {
        "host": "192.168.68.53",
        "unbind_cmds": [
            "interface GigabitEthernet1.10",
            " no ip vrf forwarding BLUE",
            "exit",
            "interface GigabitEthernet1.20",
            " no ip vrf forwarding RED",
            "exit",
            "interface Loopback10",
            " no ip vrf forwarding BLUE",
            "exit",
            "interface Loopback20",
            " no ip vrf forwarding RED",
            "exit",
        ],
        "vrf_cmds": [
            ["ip vrf BLUE", " no rd 1:1"],
            "pause",
            ["ip vrf BLUE",
             " rd 1.1.1.1:10",
             " route-target export 65000:10",
             " route-target import 65000:10",
             "exit"],
            ["ip vrf RED", " no rd 2:2"],
            "pause",
            ["ip vrf RED",
             " rd 1.1.1.1:20",
             " route-target export 65000:20",
             " route-target import 65000:20",
             "exit"]
        ],
        "rebind_cmds": [
            "interface GigabitEthernet1.10",
            " ip vrf forwarding BLUE",
            "exit",
            "interface GigabitEthernet1.20",
            " ip vrf forwarding RED",
            "exit",
            "interface Loopback10",
            " ip vrf forwarding BLUE",
            "exit",
            "interface Loopback20",
            " ip vrf forwarding RED",
            "exit",
        ]
    },
    "R2": {
        "host": "192.168.68.54",
        "unbind_cmds": [
            "interface GigabitEthernet1.10",
            " no ip vrf forwarding BLUE",
            "exit",
            "interface GigabitEthernet1.20",
            " no ip vrf forwarding RED",
            "exit",
            "interface Loopback10",
            " no ip vrf forwarding BLUE",
            "exit",
            "interface Loopback20",
            " no ip vrf forwarding RED",
            "exit",
        ],
        "vrf_cmds": [
            ["ip vrf BLUE", " no rd 1:1"],
            "pause",
            ["ip vrf BLUE",
             " rd 2.2.2.2:10",
             " route-target export 65000:10",
             " route-target import 65000:10",
             "exit"],
            ["ip vrf RED", " no rd 2:2"],
            "pause",
            ["ip vrf RED",
             " rd 2.2.2.2:20",
             " route-target export 65000:20",
             " route-target import 65000:20",
             "exit"]
        ],
        "rebind_cmds": [
            "interface GigabitEthernet1.10",
            " ip vrf forwarding BLUE",
            "exit",
            "interface GigabitEthernet1.20",
            " ip vrf forwarding RED",
            "exit",
            "interface Loopback10",
            " ip vrf forwarding BLUE",
            "exit",
            "interface Loopback20",
            " ip vrf forwarding RED",
            "exit",
        ]
    }
}

def run_block(name, conn, label, blocks):
    print(f"--- {label} on {name} ---")
    for block in blocks:
        if block == "pause":
            print(f"{name}# waiting 2 seconds for RD deletion...")
            time.sleep(2)
            continue
        output = conn.send_config_set(block, read_timeout=30)
        print(f"{name}# Sent block:\n{output}\n")

def run_phases(name, host, device):
    print(f"\nConnecting to {name} ({host})...")
    conn = ConnectHandler(
        device_type="cisco_ios",
        host=host,
        username=USERNAME,
        password=PASSWORD
    )
    conn.enable()

    conn.send_config_set(device["unbind_cmds"])
    run_block(name, conn, "Updating VRF config", device["vrf_cmds"])
    conn.send_config_set(device["rebind_cmds"])

    conn.disconnect()

if __name__ == "__main__":
    for name, device in DEVICES.items():
        run_phases(name, device["host"], device)

