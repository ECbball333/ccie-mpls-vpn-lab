from netmiko import ConnectHandler

devices = [
    {
        "name": "R1",
        "host": "192.168.68.53",
    },
    {
        "name": "R2",
        "host": "192.168.68.54",
    },
]

base_params = {
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "Cisco123",
}

commands = {
    "R1": [
        "ip route vrf BLUE 172.16.20.1 255.255.255.255 10.10.10.2",
        "ip route vrf RED 172.16.10.1 255.255.255.255 10.20.20.2",
    ],
    "R2": [
        "ip route vrf BLUE 172.16.20.1 255.255.255.255 10.10.10.1",
        "ip route vrf RED 172.16.10.1 255.255.255.255 10.20.20.1",
    ],
}

verify_cmds = [
    "show ip route vrf BLUE",
    "show ip route vrf RED",
    "ping vrf BLUE 172.16.20.1",
    "ping vrf RED 172.16.10.1"
]

for device in devices:
    conn_params = base_params.copy()
    conn_params["host"] = device["host"]
    print(f"\nConnecting to {device['name']} ({device['host']})...")
    conn = ConnectHandler(**conn_params)

    print(f"Applying route leaking config on {device['name']}...")
    for cmd in commands[device["name"]]:
        conn.send_config_set([cmd])

    print(f"\nValidating {device['name']}...")
    for vcmd in verify_cmds:
        output = conn.send_command(vcmd, expect_string=r"#", read_timeout=30)
        print(f"\n> {vcmd}\n{output}")

    conn.disconnect()

