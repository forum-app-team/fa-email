from flask import Flask
from config import Config
from extensions import mail
from flask.cli import with_appcontext
from worker import run_consumer

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)

    @app.cli.command("worker")
    @with_appcontext
    def worker():
        """Start the email queue consumer."""
        run_consumer(app=app)
    return app
