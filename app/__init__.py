# app/__init__.py
import os

from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager

from app.extensions import db
from app.models import Users
from app.filters import (
    add_days, to_date_str, date_jp, time_hm,
    datetime_jp, date_jp_full, phone, yen
)

migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # =================
    # Config
    # =================
    app.config['SECRET_KEY'] = os.urandom(24)

    base_dir = os.path.dirname(os.path.dirname(__file__))

    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(base_dir, 'data.sqlite')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True

    # =================
    # init
    # =================
    # extensions(旧db.py)初期化
    db.init_app(app)
    migrate.init_app(app, db)

    # login設定
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Users, int(user_id))

    # =================
    # filters
    # =================
    app.jinja_env.filters['add_days'] = add_days
    app.jinja_env.filters['to_date_str'] = to_date_str
    app.jinja_env.filters['date_jp'] = date_jp
    app.jinja_env.filters['time_hm'] = time_hm
    app.jinja_env.filters['datetime_jp'] = datetime_jp
    app.jinja_env.filters['date_jp_full'] = date_jp_full
    app.jinja_env.filters['phone'] = phone
    app.jinja_env.filters['yen'] = yen

    # =================
    # blueprint
    # =================
    # blueprint import (循環importを防ぐためにここでimportする)
    from app.auth.routes import auth_bp
    from app.auth.routes import auth_bp
    from app.customers.routes import customers_bp
    from app.reservations.routes import reservations_bp

    # blueprint register
    app.register_blueprint(auth_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(reservations_bp)

    return app


