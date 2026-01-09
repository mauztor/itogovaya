from flask import Flask
from .routes import init_routes

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "секретный_ключ"
    init_routes(app)
    return app