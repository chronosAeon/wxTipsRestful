from sqlalchemy import Column, Integer, String, Text
from flask_sqlalchemy import SQLAlchemy
from .__init__ import db


# anounce_db = SQLAlchemy()


class announce(db.Model):
    # id是增加主键，Unique_id是关联User主键，valid_time是有效期,announce_type有可能是声音还有可能是文字
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    valid_time = db.Column(Text)
    announce_type = db.Column(Text)
    announce_content = db.Column(Text)
