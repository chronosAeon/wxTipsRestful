import json

import requests
import time
from flask import jsonify, request
from ..models import db
from ..libs.TokenGenerator import Token_generator
from ..models.User import User
from ..models.friends import Friends
from ..models.audit_friends import audit_Friends

from . import web

__author__ = 'ChronosAeon'


# 用户：
# 用户登录登出 accomplished
# 好友列表 accomplished
# 添加好友删除好友 accomplished
# 好友添加确认列表,确认还是删除accomplished
# 事项:
# 一个人总事项，事项增删改查，通过事项id
# 别人发事项确认列表
@web.route('/resistMyFriend/<int:currentUserId>/<int:TargetUserId>')
def resistMyFriend(currentUserId, TargetUserId):
    '''
    拒绝好友申请，直接从审批表里面去除
    :param currentUserId:
    :param TargetUserId:
    :return:返回状态值
    '''
    item = db.session.query(audit_Friends).filter_by(response_user=currentUserId).filter_by(
        request_user=TargetUserId).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'res_msg': 'success', 'res_code': 200})
    else:
        return jsonify({'res_msg': 'accept_fail', 'res_code': 400})


@web.route('/acceptMyFriend/<int:currentUserId>/<int:TargetUserId>')
def acceptMyFriend(currentUserId, TargetUserId):
    '''
    接受好友申请，先从审批表去除这一条，然后在好友表添加
    :param currentUserId:
    :param TargetUserId:
    :return: 返回状态值
    '''
    item = db.session.query(audit_Friends).filter_by(response_user=currentUserId).filter_by(
        request_user=TargetUserId).first()
    if item is not None:
        db.session.delete(item)
        db.session.commit()
        '''
        好友关系添加
        '''
        friend = Friends()
        friend.firstUser = currentUserId
        friend.secondUser = TargetUserId
        db.session.add(friend)
        db.session.commit()
        return jsonify({'res_msg': 'success', 'res_code': 200})
    else:
        return jsonify({'res_msg': 'accept_fail', 'res_code': 400})


@web.route('/getMyAuditFriendsList/<int:id>')
def getMyAuditFriendsList(id):
    '''
    获取某个id的好友申请
    :param id: 查看某个id
    :return: 返回好友申请列表
    '''
    audit_group = db.session.query(audit_Friends).filter_by(response_user=id).all()
    audit_list = []
    for audit_person in audit_group:
        '''
        获取id，查找到对应的User
        '''
        friend = db.session.query(User).filter_by(id=audit_person.request_user).first()
        friend_json = json.dumps(
            {'id': friend.id, 'Unique_id': friend.Unique_id, 'account_validate': friend.account_validate,
             'Wx_userid': friend.Wx_userid, 'Wx_session': friend.Wx_session, 'name': friend.User.name,
             'portrait_url': friend.User.portrait_url})
        audit_list.append(friend_json)

    return jsonify(audit_list)


@web.route('/deleteMyFriend/<int:currentUserId>/<int:TargetUserId>')
def deleteMyFriend(currentUserId, TargetUserId):
    '''
    删除好友,是要找自己是firstUser，或者自己是secondUser
    :param currentUserId:当前使用者id
    :param TargetUserId: 被删除者id
    :return: 返回状态值
    '''
    if is_exist_by_id(User, TargetUserId):
        '''
        用户里面存在这个id
       '''
        if is_friend(currentUserId, TargetUserId):
            a_relation_ship = db.session.query(Friends).filter_by(firstUser=currentUserId).filter_by(
                secondUser=TargetUserId).first()
            other_relation_ship = db.session.query(Friends).filter_by(firstUser=TargetUserId).filter_by(
                secondUser=currentUserId).first()
            if a_relation_ship:
                db.session.delete(a_relation_ship)
                db.session.commit()
            if other_relation_ship:
                db.session.delete(other_relation_ship)
                db.session.commit()
            return jsonify({'res_msg': 'success', 'res_code': 200})
        else:
            return jsonify({'res_msg': 'fail', 'res_code': 202, 'is_friend': False})
    else:
        return jsonify({'res_msg': 'fail', 'res_code': 202, 'user_exist': False})


@web.route('/addMyFriend/<int:currentUserId>/<int:TargetUserUniqueId>')
def addMyFriend(currentUserId, TargetUserUniqueId):
    '''
    1.添加好友首先是要添加到审批表
    2.审批通过才能放进好友表
    :param currentUserId: 当前用户id
    :param TargetUserUniqueId: 添加的好友用户uniqueId
    :return: 返回状态值
    '''
    '''
    如果已经有数据库不会再添加
    '''
    u = audit_Friends()

    '''
    查找用户是否存在
    '''
    if db.session.query(User).filter_by(Unique_id=TargetUserUniqueId).first():
        '''
        获取搜索到的用户
        '''
        user = db.session.query(User).filter_by(Unique_id=TargetUserUniqueId).first()
        if not is_friend(currentUserId, user.id):
            '''
            还不是好友
            '''
            # item = db.session.query(User).filter_by(id=TargetUserUniqueId).first()
            u.request_user = currentUserId
            u.response_user = user.id
            db.session.add(u)
            db.session.commit()
            return jsonify({'res_msg': 'success', 'res_code': 200, 'is_add': True})
        else:
            '''
            已经是好友
            '''
            return jsonify({'res_msg': 'fail', 'res_code': 202, 'is_add': False})
    else:
        return jsonify({'res_msg': 'fail', 'res_code': 400, 'is_add': False})


def is_friend(currentUserId, TargetUserId):
    '''
    检查friends表检查两个人是否是朋友关系
    :param currentUserId: 当前人
    :param TargetUserId: 目标人
    :return:
    '''
    first_relation = db.session.query(Friends).filter_by(firstUser=currentUserId).filter_by(
        secondUser=TargetUserId).first()
    second_relation = db.session.query(Friends).filter_by(firstUser=TargetUserId).filter_by(
        secondUser=currentUserId).first()
    if first_relation or second_relation:
        return True
        # jsonify({'res_msg': 'success', 'res_code': 200, 'is_friend': True})
    else:
        return False


def is_exist_by_id(table, info):
    '''
    检查当前的id是否在User表中存在
    :param TargetUserId:
    :return:
    '''
    if db.session.query(table).filter_by(id=info).first():
        return True
    else:
        return False


@web.route('/getMyFriendsList/<int:id>')
def getMyFriendsList(id):
    '''
    获取某个id的好友列表,数据库不会出现1，2；2，1这种情况
    :param id: 查看某个id
    :return: 返回好友列表
    '''
    add_group = db.session.query(Friends).filter_by(firstUser=id).all()
    friends_list = []
    for add_person in add_group:
        '''
        获取id，查找到对应的User
        '''
        friend = db.session.query(User).filter_by(id=add_person.secondUser).first()
        friend_json = json.dumps(
            {'id': friend.id, 'Unique_id': friend.Unique_id, 'account_validate': friend.account_validate,
             'Wx_userid': friend.Wx_userid, 'Wx_session': friend.Wx_session, 'name': friend.name,
             'portrait_url': friend.portrait_url})
        friends_list.append(friend_json)
    # 被添加组
    added_group = db.session.query(Friends).filter_by(secondUser=id).all()
    for added_person in added_group:
        friend = db.session.query(User).filter_by(id=added_person.firstUser).first()
        friend_json = json.dumps(
            {'id': friend.id, 'Unique_id': friend.Unique_id, 'account_validate': friend.account_validate,
             'Wx_userid': friend.Wx_userid, 'Wx_session': friend.Wx_session, 'name': friend.name,
             'portrait_url': friend.portrait_url})
        friends_list.append(friend_json)
    # 这里最好去重，目前没有去重

    return jsonify(friends_list)


# 用户授权登录
@web.route('/UserLogin', methods=['POST'])
def UserLogin():
    '''
    测试完成
    :return:返回用户是否添加成功
    '''
    res = ''
    print(request.form)
    if request.method == 'POST' and request.form.get('code'):
        code = request.form.get('code')
        print(code)
        name = request.form.get('name')
        portrait_url = request.form.get('portrait_url')
        # https: // api.weixin.qq.com / sns / jscode2session?appid = APPID & secret = SECRET & js_code = JSCODE & grant_type = authorization_code
        URL_format = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'
        URL = URL_format.format(*('wx1858f8b1934f62b6', '0803387fcd3ea9a15b6f8e97637cb7f9', code))
        res = requests.get(URL)

        if res:
            '''
            code值正确
            '''
            res_dict = json.loads(res.text)
            print(res_dict)
            # 非注销过的用户
            if not db.session.query(User).filter_by(Wx_userid=res_dict['openid']).first():
                '''
                通过openid不能够拿到用户，证明用户不存在
                '''
                u = User()
                u.account_validate = True
                token_generator = Token_generator()
                token = token_generator.generate_token()
                u.Unique_id = token
                u.portrait_url = portrait_url
                u.name = name
                u.Wx_userid = res_dict['openid']
                u.Wx_session = res_dict['session_key']
                db.session.add(u)
                db.session.commit()
                return jsonify({'res_msg': 'success', 'res_code': 200, 'uniqueId': token, 'id': u.id})
            else:
                '''
                用户存在就重新接着使用
                如果是退登账号就让它可用，如果不是退登账号account_validate值改为true没有什么大毛病
                '''
                item = db.session.query(User).filter_by(Wx_userid=res_dict['openid']).first()
                item.account_validate = True
                db.session.commit()
                return jsonify({'res_msg': 'success', 'res_code': 200, 'uniqueId': item.Unique_id, 'id': item.id})
        else:
            return jsonify({'res_msg': 'error', 'res_code': 400})
    else:
        return jsonify({'res_msg': 'error', 'res_code': 400})


@web.route('/Logout/<string:id>')
def Logout(id):
    '''
    退出登录，通过uniqueId把Useidr的account_validate字段放空
    :param UniqueId: 账号唯一生成字段
    :return: 返回状态值
    '''
    user = User()
    item = db.session.query(User).filter_by(id=id).first()
    if item:
        item.account_validate = False
        db.session.commit()
        return jsonify({'res_msg': 'success', 'res_code': 200})
    else:
        return jsonify({'res_msg': 'fail', 'res_code': 400,'msg':'no_this_user'})


@web.route('/change_my_UniqueId/<string:UniqueId>/<string:NewUniqueId>')
def change_my_uniqueId(UniqueId, NewUniqueId):
    '''

    :param UniqueId: 当前用户UniqueId
    :param NewUniqueId: 新的UniqueId
    :return: 返回状态值
    '''
    person = db.session.query(User).filter_by(Unique_id=NewUniqueId).first()
    if person:
        return jsonify({'res_msg': 'fail', 'res_msg_china': '已经被注册了', 'res_code': 400})
    else:
        user = db.session.query(User).filter_by(Unique_id=UniqueId).first()
        if user:
            # user.update({'Unique_id': NewUniqueId})
            # user.update({'Unique_id_change_flag': False})
            user.Unique_id = NewUniqueId
            user.Unique_id_change_flag = False
            db.session.commit()
            return jsonify({'res_msg': 'success', 'res_msg_china': '成功修改', 'res_code': 200})
        else:
            return jsonify({'res_msg': 'fail', 'res_msg_china': '查无此账号', 'res_code': 400})


@web.route('/check_my_UniqueId/<string:UniqueId>')
def check_my_uniqueId(UniqueId):
    '''
    检查当前的UniqueId是否可用
    :param UniqueId: 要检查的UniqueId
    :return: 返回状态值
    '''
    person = db.session.query(User).filter_by(Unique_id=UniqueId).first()
    if person:
        return jsonify({'res_msg': 'fail', 'res_msg_china': '已经被注册了', 'res_code': 400})
    else:
        return jsonify({'res_msg': 'success', 'res_msg_china': '可以注册', 'res_code': 200})
