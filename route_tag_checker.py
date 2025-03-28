from netmiko import ConnectHandler

devices = [
    {
        "device_type": "cisco_ios",
        "host": "192.168.68.53",  # R1
        "username": "admin",
        "password": "Cisco123",
    },
    {
        "device_type": "cisco_ios",
        "host": "192.168.68.54",  # R2
        "username": "admin",
        "password": "Cisco123",
    }
]

commands = [
    "show ip route | include 1.1.1.1|2.2.2.2",
    "show ip ospf database external | include Tag",
    "show ip bgp | include 1.1.1.1|2.2.2.2"
]

for device in devices:
    connection = ConnectHandler(**device)
    hostname = connection.find_prompt().strip("#")

    print(f"\n--- Route Validation on {hostname} ({device['host']}) ---")
    for cmd in commands:
        output = connection.send_command(cmd)
        print(f"\n> {cmd}\n{output}")

    connection.disconnect()

