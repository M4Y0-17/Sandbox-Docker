# utils/docker_resources.py
import docker
import psutil



client = docker.from_env()


def get_container_resource_usage(container):
    """
    Obtiene el uso de recursos de un contenedor Docker específico.
    """
    stats = container.stats(stream=False)
    cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
    memory_usage = stats['memory_stats']['usage']
    return cpu_usage, memory_usage


def calculate_total_resource_usage():
    """
    Calcula el uso total de recursos de todos los contenedores Docker activos.
    """
    total_cpu_usage = 0
    total_memory_usage = 0
    for container in client.containers.list():
        cpu_usage, memory_usage = get_container_resource_usage(container)
        total_cpu_usage += cpu_usage
        total_memory_usage += memory_usage
    return total_cpu_usage, total_memory_usage


def get_system_resources():
    """
    Obtiene el uso actual de CPU y memoria de la máquina.
    """
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    return cpu_usage, memory_usage


def can_launch_new_container(additional_cpu_usage=0, additional_memory_usage=0):
    """
    Verifica si es seguro lanzar un nuevo contenedor Docker basado en el uso actual de recursos.
    """
    system_cpu, system_memory = get_system_resources()
    docker_cpu, docker_memory = calculate_total_resource_usage()
    total_cpu = system_cpu + docker_cpu
    total_memory = system_memory + docker_memory
    
    print(system_cpu)
    print(system_memory)
    print(docker_cpu)
    print(docker_memory)
    print(total_cpu)
    print(total_memory)

    cpu_limit = psutil.cpu_count() * 100 * 0.8  # 80% del total de los núcleos de CPU
    memory_limit = psutil.virtual_memory().total * 0.8  # 80% de la memoria total

    if total_cpu + additional_cpu_usage > cpu_limit or total_memory + additional_memory_usage > memory_limit:
        return False
    return True
