from utils.docker import delete_old_containers
from apscheduler.schedulers.background import BackgroundScheduler



def start_delete_old_dockers_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: delete_old_containers(app), trigger="interval", minutes=1)
    scheduler.start()
