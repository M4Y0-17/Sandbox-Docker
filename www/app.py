from flask import Flask, render_template, request, redirect, url_for
import subprocess
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import os


from utils.docker_resources import can_launch_new_container
from utils.port_manager import find_free_port, update_used_ports
from utils.docker import generate_docker_compose, get_docker_machines, delete_container, get_container_details, find_real_container_name
from utils.sheduler import start_delete_old_dockers_scheduler
from utils.models import db, DockerContainer



app = Flask(__name__)

# Ejecutar comprobador de tiempo en contenedores docker activos
start_delete_old_dockers_scheduler(app)

host_ip = os.environ.get('HOST_IP', '127.0.0.1')


#Data Base
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///docker_data.db'
db.init_app(app)  # Inicializa la instancia db con la app
with app.app_context():
    db.create_all()


@app.route('/docker-machines')
def docker_machines():
    docker_list = get_docker_machines()
    for machine in docker_list:
        creation_date = datetime.strptime(machine['creation_date'], '%Y-%m-%d %H:%M:%S')
        expiration_time = creation_date + timedelta(minutes=machine['expiration_time'])
        machine['expiration_time_in_seconds'] = (expiration_time - datetime.utcnow()).total_seconds()
    return render_template('docker_machines.html', docker_list=docker_list)


@app.route('/delete-docker/<int:container_id>', methods=['POST'])
def delete_docker_route(container_id):
    container_entry = DockerContainer.query.get(container_id)
    if container_entry and delete_container(container_entry.docker_id):
        return redirect(url_for('docker_machines'))
    else:
        return "Error al eliminar el contenedor", 500


@app.route('/container-details/<container_id>')
def container_details(container_id):
    details = get_container_details(container_id)
    return render_template('container_details.html', details=details)


@app.route('/configure-docker', methods=['GET', 'POST'])
def configure_docker():
    if request.method == 'POST':
        analyst_name = request.form['analyst_name']
        password = request.form['password']
        browser_type = request.form['browser_type']
        include_vpn = 'vpn_option' in request.form and request.form['vpn_option'] == 'yes'
        expiration_time = request.form.get('rango', type=int)

        # Obtener los puertos ya en uso
        used_ports = [container.port for container in DockerContainer.query.all()]

        # Encontrar un puerto libre
        port = find_free_port(used_ports)

        if browser_type == 'chrome':
            if include_vpn:
                template_path = 'docker-templates/chrome_vpn/docker-compose-template.txt'
            else:
                template_path = 'docker-templates/chrome/docker-compose-template.txt'
        elif browser_type == 'firefox':
            if include_vpn:
                # Devolver un error si se selecciona Firefox con Urban VPN
                return render_template('results.html', message="Firefox no tiene disponible la opción de incluir Urban VPN.", color="yellow")
            else:
                template_path = 'docker-templates/firefox/docker-compose-template.txt'
        elif browser_type == 'tor':
            if include_vpn:
                # Devolver un error si se selecciona Tor Browser con Urban VPN
                return render_template('results.html', message="Tor Browser no tiene disponible la opción de incluir Urban VPN.", color="yellow")
            else:
                template_path = 'docker-templates/tor/docker-compose-template.txt'
        elif browser_type == 'outlook':
            if include_vpn:
                template_path = 'docker-templates/chrome_outlook_vpn/docker-compose-template.txt'
            else:
                template_path = 'docker-templates/chrome_outlook/docker-compose-template.txt'
        elif browser_type == 'kali':
            if include_vpn:
                # Devolver un error si se selecciona Tor Browser con Urban VPN
                return render_template('results.html', message="Kali Linux no tiene disponible la opción de incluir Urban VPN.", color="yellow")
            else:
                template_path = 'docker-templates/kali/docker-compose-template.txt'
        elif browser_type == 'ubuntu':
            if include_vpn:
                # Devolver un error si se selecciona Tor Browser con Urban VPN
                return render_template('results.html', message="Ubuntu no tiene disponible la opción de incluir Urban VPN.", color="yellow")
            else:
                template_path = 'docker-templates/ubuntu/docker-compose-template.txt'
        else:
            return render_template('results.html', message="Opción no válida", color="yellow")

        compose_path = generate_docker_compose(template_path, port, password)

        try:
            subprocess.run(["docker-compose", "-p", f"{analyst_name}_{port}", "-f", compose_path, "up", "-d"], check=True)

            expected_name_prefix = f"{analyst_name}_{port}"
            real_container_name = find_real_container_name(expected_name_prefix)

            if real_container_name:
                url = f"https://{host_ip}:{port}"

                docker_details = get_container_details(real_container_name)
                
                if docker_details:
                    creation_date = docker_details['creation_date']

                    port_mappings = docker_details['ports']
                    host_port = next((mapping['HostPort'] for port, mappings in port_mappings.items() 
                                      if mappings for mapping in mappings 
                                      if mapping and 'HostPort' in mapping), None)

                    new_container = DockerContainer(docker_id=real_container_name,
                                                    name=docker_details['name'],
                                                    creation_date=creation_date,
                                                    port=host_port,
                                                    url=url,
                                                    expiration_time=expiration_time)
                    db.session.add(new_container)
                    db.session.commit()
                    message = f"Contenedor iniciado. Acceda a través de: {url}"
                    return render_template('results.html', message=message, color="blue")
                else:
                    message = "Error: No se pudo encontrar el contenedor recién creado. 1"
                    return render_template('results.html', message=message, color="red")
            else:
                message = "Error: No se pudo encontrar el contenedor recién creado. 2"
                return render_template('results.html', message=message, color="red")
        except subprocess.CalledProcessError as e:
            message = f"Error al iniciar el contenedor: {e.stderr}"
            return render_template('results.html', message=message, color="red")
        except IntegrityError:
            db.session.rollback()
            return render_template('results.html', message="Error: Un contenedor con ese ID ya existe.", color="red")

    return render_template('configure_docker.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    # puedes elegir entre devolver solo un mensaje simple,
    # return 'Esta página no fue encontrada', 404
    
    # o devolver una plantilla HTML
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
