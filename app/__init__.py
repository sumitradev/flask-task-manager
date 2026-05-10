from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = False

    # Initialise extensions
    db.init_app(app)
    metrics = PrometheusMetrics(app)

    # Register routes
    from app.routes import tasks_bp
    app.register_blueprint(tasks_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app