from netmiko import ConnectHandler
from getpass import getpass
from dotenv import load_dotenv
import os
import time

load_dotenv()

USERNAME = os.getenv("USERNAME") or input("Username: ")
PASSWORD = os.getenv("PASSWORD") or getpass("Password: ")

DEVICE_BLOCKS = {
    "R1": {
        "host": "192.168.68.53",
        "blocks": [
            [
                "vrf definition BLUE",
                " rd 1.1.1.1:10",
                " route-target export 65000:10",
                " route-target import 65000:10",
                "exit",
                "vrf definition RED",
                " rd 1.1.1.1:20",
                " route-target export 65000:20",
                " route-target import 65000:20",
                "exit",
            ],
            [
                "interface Loopback10",
                " ip vrf forwarding BLUE",
                " ip address 172.16.10.1 255.255.255.255",
                "exit",
                "interface Loopback20",
                " ip vrf forwarding RED",
                " ip address 172.16.20.1 255.255.255.255",
                "exit",
            ],
            [
                "router bgp 65001",
                " bgp router-id 1.1.1.1",
                " no bgp default ipv4-unicast",
                " bgp log-neighbor-changes",
                " address-family vpnv4",
                "  neighbor 2.2.2.2 remote-as 65002",
                "  neighbor 2.2.2.2 update-source Loopback0",
                "  neighbor 2.2.2.2 activate",
                "  neighbor 2.2.2.2 send-community extended",
                " exit-address-family",
                " address-family ipv4 vrf BLUE",
                "  redistribute connected",
                " exit-address-family",
                " address-family ipv4 vrf RED",
                "  redistribute connected",
                " exit-address-family",
            ]
        ]
    },
    "R2": {
        "host": "192.168.68.54",
        "blocks": [
            [
                "vrf definition BLUE",
                " rd 2.2.2.2:10",
                " route-target export 65000:10",
                " route-target import 65000:10",
                "exit",
                "vrf definition RED",
                " rd 2.2.2.2:20",
                " route-target export 65000:20",
                " route-target import 65000:20",
                "exit",
            ],
            [
                "interface Loopback10",
                " ip vrf forwarding BLUE",
                " ip address 172.16.10.2 255.255.255.255",
                "exit",
                "interface Loopback20",
                " ip vrf forwarding RED",
                " ip address 172.16.20.2 255.255.255.255",
                "exit",
            ],
            [
                "router bgp 65002",
                " bgp router-id 2.2.2.2",
                " no bgp default ipv4-unicast",
                " bgp log-neighbor-changes",
                " address-family vpnv4",
                "  neighbor 1.1.1.1 remote-as 65001",
                "  neighbor 1.1.1.1 update-source Loopback0",
                "  neighbor 1.1.1.1 activate",
                "  neighbor 1.1.1.1 send-community extended",
                " exit-address-family",
                " address-family ipv4 vrf BLUE",
                "  redistribute connected",
                " exit-address-family",
                " address-family ipv4 vrf RED",
                "  redistribute connected",
                " exit-address-family",
            ]
        ]
    }
}

VERIFY_COMMANDS = [
    "show bgp vpnv4 unicast all summary",
    "show bgp vpnv4 unicast all",
    "ping vrf BLUE 172.16.10.2",
    "ping vrf RED 172.16.20.2"
]

def push_config_blocks(name, host, blocks):
    print(f"\nConnecting to {name} ({host})...")
    conn = ConnectHandler(
        device_type="cisco_ios",
        host=host,
        username=USERNAME,
        password=PASSWORD,
        session_log=f"{name}_session_log.txt"
    )

    for i, block in enumerate(blocks, 1):
        print(f"Sending block {i} to {name}...")
        try:
            output = conn.send_config_set(block, read_timeout=90)
            print(f"Output from block {i} on {name}:
{output}")
        except Exception as e:
            print(f"[ERROR] Block {i} failed on {name}: {e}")
        time.sleep(1)

    return conn

def validate(name, conn):
    print(f"\nValidating {name}...")
    for cmd in VERIFY_COMMANDS:
        output = conn.send_command_timing(cmd)
        print(f"\n> {cmd}\n{output}")
    conn.disconnect()

if __name__ == "__main__":
    for name, device in DEVICE_BLOCKS.items():
        conn = push_config_blocks(name, device["host"], device["blocks"])
        validate(name, conn)

