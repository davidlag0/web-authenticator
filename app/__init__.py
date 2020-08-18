from flask import Flask
from datetime import timedelta
import os
from app.auth.helper import SESSION_EXPIRATION
from app.auth import auth_blueprint


# Application Factory.
def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)
    app.permanent_session_lifetime = timedelta(minutes=SESSION_EXPIRATION)
    register_blueprints(app)

    # TODO: Investigate further how to use this.
    # Dynamically load config based on the testing argument or FLASK_ENV environment variable
    """
    flask_env = os.getenv("FLASK_ENV", None)
    if testing:
        app.config.from_object(config.TestingConfig)
    elif flask_env == "development":
        app.config.from_object(config.ProductionConfig)
    elif flask_env == "testing":
        app.config.from_object(config.TestingConfig)
    else:
        app.config.from_object(config.ProductionConfig)
    """

    # Bind to PORT if defined, otherwise default to 6000.
    #port = int(os.environ.get('PORT', 6000))
    #app.run(host='0.0.0.0', port=port, debug=True)

    return app

def register_blueprints(app):
    # Register each Blueprint with the Flask application
    # instance (app)
    app.register_blueprint(auth_blueprint)
