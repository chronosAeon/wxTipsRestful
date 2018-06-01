from sqlalchemy import Column, Integer, UniqueConstraint

from .__init__ import db


class Friends(db.Model):
    # 好友关系id，用户1，用户2
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstUser = db.Column(db.Integer, db.ForeignKey('user.id'))
    secondUser = db.Column(db.Integer, db.ForeignKey('user.id'))
    __table_args__ = (UniqueConstraint('firstUser', 'secondUser', name='friendship'),)
