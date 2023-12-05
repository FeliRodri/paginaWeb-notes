from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO



db = SQLAlchemy()
DB_NAME = "databasetest.db"

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'probando_clave-secreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    socketio = SocketIO(app)

    from .views import views
    from .auth import auth
    from .models import User, Note

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        create_database()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    migrate = Migrate(app, db)

    return app

def create_database():
    if not path.exists('website/' + DB_NAME):
        db.create_all()
        print('Created Database!')




