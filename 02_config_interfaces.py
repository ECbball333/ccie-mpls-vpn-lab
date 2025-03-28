from netmiko import ConnectHandler
from getpass import getpass
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("USERNAME") or input("Username: ")
PASSWORD = os.getenv("PASSWORD") or getpass("Password: ")

DEVICE_CONFIGS = {
    "R1": {
        "host": "192.168.68.53",
        "commands": [
            "interface Loopback10",
            " ip address 172.16.10.1 255.255.255.255",
            " ip vrf forwarding BLUE",
            "exit",
            "interface Loopback20",
            " ip address 172.16.20.1 255.255.255.255",
            " ip vrf forwarding RED",
            "exit",
            "interface GigabitEthernet1.10",
            " encapsulation dot1Q 10",
            " ip address 10.10.10.1 255.255.255.252",
            " ip vrf forwarding BLUE",
            " no shutdown",
            "exit",
            "interface GigabitEthernet1.20",
            " encapsulation dot1Q 20",
            " ip address 10.20.20.1 255.255.255.252",
            " ip vrf forwarding RED",
            " no shutdown",
            "exit"
        ]
    },
    "R2": {
        "host": "192.168.68.54",
        "commands": [
            "interface Loopback10",
            " ip address 172.16.10.2 255.255.255.255",
            " ip vrf forwarding BLUE",
            "exit",
            "interface Loopback20",
            " ip address 172.16.20.2 255.255.255.255",
            " ip vrf forwarding RED",
            "exit",
            "interface GigabitEthernet1.10",
            " encapsulation dot1Q 10",
            " ip address 10.10.10.2 255.255.255.252",
            " ip vrf forwarding BLUE",
            " no shutdown",
            "exit",
            "interface GigabitEthernet1.20",
            " encapsulation dot1Q 20",
            " ip address 10.20.20.2 255.255.255.252",
            " ip vrf forwarding RED",
            " no shutdown",
            "exit"
        ]
    }
}

def configure_interfaces(name, host, commands):
    print(f"\nConnecting to {name} ({host})...")
    conn = ConnectHandler(
        device_type="cisco_ios",
        host=host,
        username=USERNAME,
        password=PASSWORD
    )
    conn.enable()
    print(f"Applying interface config to {name}...")
    output = conn.send_config_set(commands)
    print(output)
    conn.disconnect()

if __name__ == "__main__":
    for name, device in DEVICE_CONFIGS.items():
        configure_interfaces(name, device["host"], device["commands"])

