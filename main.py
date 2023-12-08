from website import create_app
from website.views import views
from website.auth import socketio
from website.models import db
from website.scheduler import init_scheduler
from config import config


app = create_app()
init_scheduler(app)
app.register_blueprint(views, url_prefix='/', name=views)

socketio.init_app(app)

if __name__ == '__main__':
    app.config.from_object(config['development'])
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
    