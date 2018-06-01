from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean
from .__init__ import db
# 关系批准表
class audit_Friends(db.Model):
    # 好友关系id，用户1，用户2
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    response_user = db.Column(db.Integer, db.ForeignKey('user.id'))