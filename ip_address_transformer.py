def ip_to_int(ip: str) -> int:
    parts = ip.split('.')
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])


def int_to_ip(ip_int) -> str:
    return '.'.join(str((ip_int >> i) & 0xFF) for i in [24, 16, 8, 0])

def ip_to_hex(ip) -> str:
    hex_ip = '0x'+''.join(hex(int(x))[2:].zfill(2) for x in ip.split('.'))
    return hex_ip

if __name__ == "__main__":
    ip = '127.0.0.1'
    ip_hex = ip_to_int(ip)
    print(ip_hex)

    ip_int = 2130706433
    ip = int_to_ip(ip_int)
    print(ip)
