from flask import Flask, render_template, request, redirect, url_for
import subprocess
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import os
import re
import shutil


from utils.docker_resources import can_launch_new_container
from utils.port_manager import find_free_port, update_used_ports
from utils.docker import generate_docker_compose, get_docker_machines, delete_container, get_container_details, find_real_container_name
from utils.sheduler import start_delete_old_dockers_scheduler
from utils.tools import is_email_content
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


UPLOAD_FOLDER = './file_transfer'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = UPLOAD_FOLDER + "/tmpfiles/"


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
    if container_entry:
        # Usa el path almacenado en la base de datos
        container_dir_path = container_entry.directory_path

        # Elimina el contenedor usando Docker
        if delete_container(container_entry.docker_id):
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

        if browser_type == 'chrome':
            if 'eml_file' in request.files and request.files['eml_file'].filename != '':
                return render_template('results.html', message="Actualmente Chrome no acepta la subida de archivos.", color="yellow")
            elif include_vpn:
                template_path = 'docker-templates/chrome_vpn/docker-compose-template.txt'
            else:
                template_path = 'docker-templates/chrome/docker-compose-template.txt'
        elif browser_type == 'firefox':
            if 'eml_file' in request.files and request.files['eml_file'].filename != '':
                return render_template('results.html', message="Actualmente Firefox no acepta la subida de archivos.", color="yellow")
            elif include_vpn:
                return render_template('results.html', message="Firefox no tiene disponible la opción de incluir Urban VPN.", color="yellow")
            else:
                template_path = 'docker-templates/firefox/docker-compose-template.txt'
        elif browser_type == 'tor':
            if 'eml_file' in request.files and request.files['eml_file'].filename != '':
                return render_template('results.html', message="Actualmente Tor Browser no acepta la subida de archivos.", color="yellow")
            elif include_vpn:
                return render_template('results.html', message="Tor Browser no tiene disponible la opción de incluir Urban VPN.", color="yellow")
            else:
                template_path = 'docker-templates/tor/docker-compose-template.txt'
        elif browser_type == 'outlook':
            if 'eml_file' in request.files and request.files['eml_file'].filename != '':
                return render_template('results.html', message="Actualmente Outlook no acepta la subida de archivos.", color="yellow")
            elif include_vpn:
                template_path = 'docker-templates/chrome_outlook_vpn/docker-compose-template.txt'
            else:
                template_path = 'docker-templates/chrome_outlook/docker-compose-template.txt'
        elif browser_type == 'kali':
            if 'eml_file' in request.files and request.files['eml_file'].filename != '':
                return render_template('results.html', message="Actualmente Kali Linux no acepta la subida de archivos.", color="yellow")
            elif include_vpn:
                return render_template('results.html', message="Kali Linux no tiene disponible la opción de incluir Urban VPN.", color="yellow")
            else:
                template_path = 'docker-templates/kali/docker-compose-template.txt'
        elif browser_type == 'ubuntu':
            if 'eml_file' in request.files and request.files['eml_file'].filename != '':
                return render_template('results.html', message="Actualmente Ubuntu no acepta la subida de archivos.", color="yellow")
            elif include_vpn:
                return render_template('results.html', message="Ubuntu no tiene disponible la opción de incluir Urban VPN.", color="yellow")
            else:
                template_path = 'docker-templates/ubuntu/docker-compose-template.txt'
        elif browser_type == 'thunderbird':
            # Verifica si se incluyó el archivo .eml y si este tiene un nombre de archivo.
            if 'eml_file' not in request.files or request.files['eml_file'].filename == '':
                # Si no se sube un archivo .eml, retorna un mensaje de error.
                return render_template('results.html', message="Por favor, suba un archivo .eml para continuar con Thunderbird.", color="yellow")
            elif include_vpn:
                return render_template('results.html', message="Thunderbird no tiene disponible la opción de incluir Urban VPN.", color="yellow")
            else:
                template_path = 'docker-templates/thunderbird/docker-compose-template.txt'
        else:
            return render_template('results.html', message="Opción no válida", color="yellow")


        # Comprobaciones de seguridad para los parametros del formulario
        if expiration_time < 3 or expiration_time > 90:
            # Si no está dentro del rango, salta un error
            return render_template('results.html', message="El tiempo de expiración debe estar entre 3 y 90 minutos.", color="yellow")

        if not analyst_name or not re.match(r'^[a-zA-Z\s]+$', analyst_name):
            # Si el nombre está en blanco o contiene caracteres no permitidos, devolver un mensaje de error
            return render_template('results.html', message="El nombre del analista solo puede contener letras y no puede estar en blanco.", color="yellow")

        if not re.match(r'^[^ ]+$', password):
            return render_template('results.html', message="La contraseña no puede estar en blanco ni contener espacios.", color="yellow")

        # Inicializa eml_file_path y container_dir_path como None fuera del bloque if
        eml_file_path = None
        container_dir_path = None

        # Verifica si se ha subido un archivo y procesa según corresponda
        if 'eml_file' in request.files and request.files['eml_file'].filename != '':
            eml_file = request.files['eml_file']
            filename = secure_filename(eml_file.filename)

            # Guarda el archivo en una ubicación temporal para verificar su tipo MIME
            creation_date_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S-%f")
            container_dir_name = f"{analyst_name}_{creation_date_str}"
            temp_file_path = app.config['TEMP_FOLDER'] + container_dir_name
            os.makedirs(temp_file_path, exist_ok=True)
            temp_file_path = os.path.join(temp_file_path, filename)
            eml_file.save(temp_file_path)

            # Comprobar si el contenido del archivo es el de un correo
            if is_email_content(temp_file_path):
                container_dir_path = os.path.join(app.config['UPLOAD_FOLDER'], container_dir_name)
                os.makedirs(container_dir_path, exist_ok=True)
                eml_file_path = os.path.join(container_dir_path, filename)
                # Restablecer el puntero del archivo antes de guardar por segunda vez
                eml_file.seek(0)
                eml_file.save(eml_file_path)
                eml_file_path = "../../file_transfer/" + container_dir_name + "/" + filename
                # Esto dará la ruta del directorio que contiene el archivo
                directory_path = os.path.dirname(temp_file_path)
                shutil.rmtree(directory_path)
            else:
                # Esto dará la ruta del directorio que contiene el archivo
                directory_path = os.path.dirname(temp_file_path)
                shutil.rmtree(directory_path)
                return render_template('results.html', message="El archivo subido no es un archivo de correo electrónico.", color="yellow")

        # Obtener los puertos ya en uso
        used_ports = [container.port for container in DockerContainer.query.all()]

        # Encontrar un puerto libre
        port = find_free_port(used_ports)

        try:
            if eml_file_path is not None:
                # Llama a generate_docker_compose incluyendo el eml_file_path
                compose_path = generate_docker_compose(template_path, port, password, eml_file_path)
            else:
                # Llama a generate_docker_compose sin el eml_file_path
                compose_path = generate_docker_compose(template_path, port, password)
            subprocess.run(["docker-compose", "-p", f"{analyst_name}_{port}", "-f", compose_path, "up", "-d"], check=True)

            real_container_name = find_real_container_name(f"{analyst_name}_{port}")
            if real_container_name:
                docker_details = get_container_details(real_container_name)
                url = f"https://{host_ip}:{port}"
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
                                                    expiration_time=expiration_time,
                                                    directory_path=container_dir_path if container_dir_path else None)
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


@app.errorhandler(Exception)
def handle_error(e):
    # Verifica si el código de error está en el rango de errores del cliente (400-499)
    if 400 <= e.code < 500:
        return render_template('4xx.html', error_code=e.code), e.code
    else:
        # Asegúrate de que la carpeta de logs existe
        log_directory = "error_logs"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        # Manejo de errores: guarda el log y muestra la página de error
        log_filename = f"{log_directory}/log_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}.txt"
        with open(log_filename, 'w') as log_file:
            log_file.write(f"Time: {datetime.now().isoformat()}\n")
            log_file.write(f"Error: {e}\n")
        
        return render_template('5xx.html', error_code=e.code), e.code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
