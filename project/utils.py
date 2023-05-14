from celery import Celery


def make_celery(app) -> Celery:
    """
    Create a Celery instance and configure it to run tasks within the Flask web-crawler-service context.

    :param app: Flask application instance.
    :return: Initialized Celery instance.
    """
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY_CONFIG"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
