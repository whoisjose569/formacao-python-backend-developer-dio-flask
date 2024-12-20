import os

from flask import Flask
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from src.models.base import db
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
ma = Marshmallow()

spec = APISpec(
    title="DIO BLOG",
    version="1.0.0",
    openapi_version="3.0.3",
    info=dict(description="DIO BLOG API"),
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

def create_app(environment=os.getenv("ENVIRONMENT", "development")):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(f"src.config.{environment.title()}Config")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    
    from src.controllers import user
    from src.controllers import auth
    
    app.register_blueprint(user.bp)
    app.register_blueprint(auth.bp)
    
    @app.route('/docs')
    def docs():
        return spec.path(view=user.get_user).path(view=user.delete_user).to_dict()
    
    from flask import json
    from werkzeug.exceptions import HTTPException
    
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        response = e.get_response()
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response
    
    
    return app