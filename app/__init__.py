from flask import Flask
from app.models.__init__ import db
from app.models import User, friends, audit_friends, announce, audit_announce
# import app.models.User
# import app.models.announce


def create_app():
    app = Flask(__name__)  # type:Flask
    # 读取配置文件
    app.config.from_object('app.secure')
    app.config.from_object('app.setting')
    # 注册蓝图
    register_blueprint(app)

    # 这个方法只是读取app.config的数据库配置文件
    db.init_app(app)
    # 方法一获取app
    # db.create_all(app=app)
    # 方法二通过上下文管理器推入核心appcontext
    with app.app_context():
        db.create_all(app=app)
    return app


def register_blueprint(app):
    from app.web import web
    # from app.web.user import user
    app.register_blueprint(web)
