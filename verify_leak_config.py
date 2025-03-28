from netmiko import ConnectHandler
from getpass import getpass
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("USERNAME") or input("Username: ")
PASSWORD = os.getenv("PASSWORD") or getpass("Password: ")

DEVICES = {
    "R1": {
        "host": "192.168.68.53",
        "commands": [
            "router ospf 100 vrf BLUE",
            "redistribute static",
            "exit",
            "router ospf 200 vrf RED",
            "redistribute static",
            "exit",
            "ip route vrf BLUE 172.16.20.1 255.255.255.255 10.10.10.2",
            "ip route vrf RED 172.16.10.1 255.255.255.255 10.20.20.2",
        ]
    },
    "R2": {
        "host": "192.168.68.54",
        "commands": [
            "router ospf 100 vrf BLUE",
            "redistribute static",
            "exit",
            "router ospf 200 vrf RED",
            "redistribute static",
            "exit",
            "ip route vrf BLUE 172.16.20.1 255.255.255.255 10.10.10.1",
            "ip route vrf RED 172.16.10.1 255.255.255.255 10.20.20.1",
        ]
    }
}

VERIFY_COMMANDS = [
    "show ip route vrf BLUE",
    "show ip route vrf RED",
    "ping vrf BLUE 172.16.10.1",
    "ping vrf RED 172.16.20.1"
]

def configure_device(name, host, config_commands):
    print(f"\nConnecting to {name} ({host})...")
    connection = ConnectHandler(
        device_type="cisco_ios",
        host=host,
        username=USERNAME,
        password=PASSWORD
    )
    print(f"Applying configuration on {name}...")
    connection.send_config_set(config_commands)
    return connection

def verify_device(name, connection):
    print(f"\nValidating {name}...")
    for cmd in VERIFY_COMMANDS:
        if cmd.startswith("ping"):
            output = connection.send_command_timing(cmd)
            print(f"\n> {cmd}\n{output}")
            if "!!!!!" in output or "Success rate is 100 percent" in output:
                print(f"[PASS] Ping succeeded for {cmd}")
            else:
                print(f"[FAIL] Ping failed for {cmd}")
        else:
            output = connection.send_command(cmd, expect_string=r"#", read_timeout=30)
            print(f"\n> {cmd}\n{output}")
    connection.disconnect()

if __name__ == "__main__":
    for name, device in DEVICES.items():
        conn = configure_device(name, device["host"], device["commands"])
        verify_device(name, conn)

