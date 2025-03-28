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
        "asn": 65001,
        "router_id": "1.1.1.1",
        "neighbor_ip": "2.2.2.2",
        "neighbor_as": 65002,
        "vrfs": {
            "BLUE": ["redistribute connected"],
            "RED": ["redistribute connected"]
        }
    },
    "R2": {
        "host": "192.168.68.54",
        "asn": 65002,
        "router_id": "2.2.2.2",
        "neighbor_ip": "1.1.1.1",
        "neighbor_as": 65001,
        "vrfs": {
            "BLUE": ["redistribute connected"],
            "RED": ["redistribute connected"]
        }
    }
}

def generate_bgp_commands(asn, router_id, neighbor_ip, neighbor_as, vrfs):
    commands = [
        f"router bgp {asn}",
        f" bgp router-id {router_id}",
        f" neighbor {neighbor_ip} remote-as {neighbor_as}",
        f" neighbor {neighbor_ip} update-source Loopback0",
        " address-family vpnv4",
        f"  neighbor {neighbor_ip} activate",
        f"  neighbor {neighbor_ip} send-label",
        " exit-address-family"
    ]

    for vrf, vrf_cmds in vrfs.items():
        commands.append(f" address-family ipv4 vrf {vrf}")
        commands.extend([f"  {cmd}" for cmd in vrf_cmds])
        commands.append(" exit-address-family")

    return commands

def configure_bgp(name, host, config):
    print(f"\nConnecting to {name} ({host})...")
    conn = ConnectHandler(
        device_type="cisco_ios",
        host=host,
        username=USERNAME,
        password=PASSWORD
    )
    conn.enable()

    commands = generate_bgp_commands(
        asn=config["asn"],
        router_id=config["router_id"],
        neighbor_ip=config["neighbor_ip"],
        neighbor_as=config["neighbor_as"],
        vrfs=config["vrfs"]
    )

    print(f"Applying BGP config to {name}...")
    output = conn.send_config_set(commands)
    print(output)

    conn.disconnect()

if __name__ == "__main__":
    for name, device in DEVICE_CONFIGS.items():
        configure_bgp(name, device["host"], device)

