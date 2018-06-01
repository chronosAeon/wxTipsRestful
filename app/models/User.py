from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean
from flask_sqlalchemy import SQLAlchemy
from .__init__ import db


# 方法三 实例化SQLAlchemy的时候构造函数是有app可选参数的，会存贮在内部
# db = SQLAlchemy()


class User(db.Model):
    # 面对程序:用户id,UserId 面向连接:用户token 面对微信:,Wx_userid,Wx_unionid
    # 用户和声明是一对多
    id = Column(Integer, primary_key=True, autoincrement=True)
    Unique_id = Column(String(50), unique=True)
    account_validate = Column(Boolean, nullable=False, default=True)
    Wx_userid = Column(String(50),unique=True)
    Wx_session = Column(String(50))
    name = Column(Text)
    portrait_url = Column(Text)
    Unique_id_change_flag = Column(Boolean, nullable=False, default=True)
    anounces = db.relationship('announce', backref=db.backref('User'))
    # friends = db.relationship('friends', backref=db.backref('User'))