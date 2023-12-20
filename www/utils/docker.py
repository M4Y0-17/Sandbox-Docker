import os
import re
import docker
import time
from datetime import datetime, timedelta
from flask import current_app


from utils.models import DockerContainer, db



client = docker.from_env()


def generate_docker_compose(template_path, port, password):
    with open(template_path, 'r') as file:
        template = file.read()

    service_name = f"chrome_{port}"  # Genera un nombre de servicio único
    config = re.sub(r'service_name:\s*\w+', f'service_name: {service_name}', template)
    config = config.replace("${PORT}", str(port)).replace("${PASSWORD}", password)
    output_path = os.path.join(os.path.dirname(template_path), 'docker-compose.yml')

    with open(output_path, 'w') as file:
        file.write(config)

    return output_path


def get_docker_machines():
    # Suponiendo que DockerContainer es un modelo de SQLAlchemy
    docker_machines = DockerContainer.query.all()
    return [
        {
            'id': container.id, 
            'name': container.name, 
            'creation_date': container.creation_date.strftime('%Y-%m-%d %H:%M:%S'), 
            'port': container.port, 
            'url': container.url,
            'expiration_time': container.expiration_time  # Asegúrate de incluir esto
        } for container in docker_machines
    ]



def delete_container(container_name, max_retries=5, wait_seconds=5):
    client = docker.from_env()
    container_deleted = False  # Flag para verificar si el contenedor fue eliminado con éxito

    try:
        # Busca el contenedor por su nombre
        container = client.containers.get(container_name)
        image_name = container.image.tags[0] if container.image.tags else None  # Obtener el nombre de la imagen

        container.stop()
        container.remove()
        container_deleted = True  # Indica que el contenedor se eliminó con éxito

        # Intenta eliminar la imagen varias veces si existe
        if image_name:
            for attempt in range(max_retries):
                try:
                    client.images.remove(image_name)
                    print(f"Imagen {image_name} eliminada con éxito.")
                    break
                except docker.errors.ImageNotFound:
                    print(f"La imagen {image_name} ya ha sido eliminada.")
                    break
                except docker.errors.APIError as e:
                    print(f"No se pudo eliminar la imagen {image_name}: {e}. Reintentando...")
                    time.sleep(wait_seconds)

    except docker.errors.NotFound:
        print(f"El contenedor {container_name} no existe o ya ha sido eliminado.")
        container_deleted = True

    except Exception as e:
        print(f"Error al eliminar el contenedor {container_name}: {e}")

    # Elimina la entrada del contenedor de la base de datos si existe y si el contenedor fue eliminado con éxito
    if container_deleted:
        with current_app.app_context():
            container_entry = DockerContainer.query.filter_by(docker_id=container_name).first()
            if container_entry:
                db.session.delete(container_entry)
                db.session.commit()
                print(f"Entrada de la base de datos para el contenedor {container_name} eliminada con éxito.")

    return container_deleted


def delete_old_containers(app):
    with app.app_context():
        client = docker.from_env()
        containers = client.containers.list()

        for container in containers:
            # Asegúrate de que el identificador usado aquí coincida con el de la base de datos
            docker_container = DockerContainer.query.filter_by(docker_id=container.name).first()
            if docker_container:
                created_time = datetime.strptime(container.attrs['Created'][:26] + 'Z', '%Y-%m-%dT%H:%M:%S.%fZ')
                expiration_minutes = docker_container.expiration_time
                if datetime.utcnow() - created_time > timedelta(minutes=expiration_minutes):
                    delete_container(container.name)  # Asegúrate de que este es el identificador correcto


def get_container_details(container_id):
    try:
        container = client.containers.get(container_id)
        stats = container.stats(stream=False)
        
        # Extrae los detalles específicos
        id = container.id
        name = container.name
        ports = container.ports
        cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
        memory_usage = stats['memory_stats']['usage']
        memory_limit = stats['memory_stats']['limit']
        memory_usage_percent = (memory_usage / memory_limit) * 100 if memory_limit else 0
        
        # Ajusta la fecha de creación para manejar nanosegundos
        created_str = container.attrs['Created']
        # Trunca los nanosegundos a microsegundos (6 dígitos)
        creation_date = datetime.strptime(created_str[:26], '%Y-%m-%dT%H:%M:%S.%f')

        return {
            'id': id,
            'name': name,
            'ports': ports,
            'creation_date': creation_date,  # Añadido la fecha de creación aquí
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'memory_usage_percent': memory_usage_percent
            # Añade aquí más detalles si es necesario
        }
    except Exception as e:
        print(f"Error al obtener detalles del contenedor {container_id}: {e}")
        return None


def find_real_container_name(expected_name_prefix):
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        if container.name.startswith(expected_name_prefix):
            return container.name
    return None
