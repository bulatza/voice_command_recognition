import socket
import fcntl
import struct

def get_ip_adress(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def primary_ip_adress():
    ip_adress = get_ip_adress('lo')
    try:
	ip_adress = get_ip_adress('eth0')
    except Exception:
	pass
    
    try:
	ip_adress = get_ip_adress('wlan0')
    except Exception:
	pass
    
    return ip_adress
