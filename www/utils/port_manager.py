import socket
import docker



client = docker.from_env()


def update_used_ports(container_id):
    container = client.containers.get(container_id)
    ports = container.attrs['NetworkSettings']['Ports']
    used_ports = [int(port.split(':')[1]) for port in ports.keys() if port is not None]
    return used_ports


def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0


def find_free_port(used_ports):
    for port in range(6902, 6999):
        if port not in used_ports:
            return port
    raise Exception("No free ports available")

