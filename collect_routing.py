from netmiko import ConnectHandler
from datetime import datetime

# Device definitions
devices = [
    {
        "device_type": "cisco_ios",
        "host": "192.168.68.53",  # R1 IP
        "username": "admin",
        "password": "Cisco123",
    },
    {
        "device_type": "cisco_ios",
        "host": "192.168.68.54",  # R2 IP
        "username": "admin",
        "password": "Cisco123",
    }
]

commands = [
    "show ip route",
    "show ip bgp",
    "show ip ospf database",
    "show ip eigrp topology"
]

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

for device in devices:
    connection = ConnectHandler(**device)
    hostname = connection.find_prompt().replace("#", "").strip()
    log_file = f"{hostname}_routing_log_{timestamp}.txt"

    with open(log_file, "w") as f:
        f.write(f"==== Output from {hostname} ====\n\n")
        for cmd in commands:
            output = connection.send_command(cmd)
            f.write(f"--- {cmd} ---\n{output}\n\n")

    connection.disconnect()
    print(f"[+] Saved routing output to {log_file}")

