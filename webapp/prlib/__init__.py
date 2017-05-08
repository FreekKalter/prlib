from flask import Flask
from celery import Celery


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('flask.cfg')

# configure celery with flask app context
celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
TaskBase = celery.Task
class ContextTask(TaskBase):
    abstract = True
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)
celery.Task = ContextTask

from . import views, prlib
