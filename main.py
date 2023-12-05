from website import create_app
from website.views import views
from website.auth import socketio
from website.models import db
from website.scheduler import init_scheduler

app = create_app()
init_scheduler(app)
app.register_blueprint(views, url_prefix='/', name=views)

socketio.init_app(app)

if __name__ == '__main__':
    print(app.url_map)
    socketio.run(app, debug=True)