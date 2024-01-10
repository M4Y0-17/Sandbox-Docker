from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()


class DockerContainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    docker_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(200), nullable=False)
    expiration_time = db.Column(db.Integer, nullable=False)  # Tiempo en minutos

    def __repr__(self):
        return f'<DockerContainer {self.name}>'
