import socket



def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0


def find_free_port():
    for port in range(6902, 6999):
        if is_port_free(port):
            return port
    raise Exception("No free ports available")
