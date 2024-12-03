#!/usr/bin/env python3

import socket

def get_local_ip():
    # connect to something and grab our local address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

local_ip = get_local_ip()

with open('.env', 'w') as f:
    f.write(f'HOST_IP={local_ip}')
