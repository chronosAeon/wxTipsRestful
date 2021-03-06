import json
import os
import time

from flask import jsonify, request

from . import web

__author__ = 'ChronosAeon'
from ..models import db
from ..models.audit_announce import audit_announce
from ..models.announce import announce


# 事项:
# 一个人总事项。accomplished
# 指定事项增删改查，通过事项id,和 userid accomplished
# 给别人发的事项
# 别人发的事项确认

# completed
@web.route('/getAnnouncesById/<int:userId>')
def getAnnouncesById(userId):
    '''
    获取指定id账户的所有公告
    :param userId:账户id
    :return: 账户的所有的announce数据
    '''
    Announce_group = db.session.query(announce).filter_by(user_id=userId).all()
    Announce_list = []
    for Announce in Announce_group:
        Announce_json = json.dumps(
            {'id': Announce.id, 'user_id': Announce.user_id, 'valid_time': Announce.valid_time,
             'announce_type': Announce.announce_type, 'announce_content': Announce.announce_content})
        Announce_list.append(Announce_json)
    return jsonify(Announce_list)


# completed
@web.route('/modifyAnnounceById/<int:userId>/<int:announceId>')
def modifyAnnounceById(userId, announceId):
    '''
    使用了wx小程序upload接口
    :param userId:当前使用者的id
    :param announceId: 当前修改公告的id
    :param type:公告内容的数据类型
    :param announce:修改后的公告数据
    :return: 状态值
    '''
    '''
    类型是音频上传
    '''
    if request.form['announce_type'] == 'audio':
        audio = request.files['audio']
        item = db.session.query(announce).filter_by(user_id=userId).filter_by(id=announceId).first()
        if item:
            '''
            找到对应的项目
            声音文件存在服务器的static里面，然后是uuid编码，然后返回文件位置。
            名字就是unix时间戳加上文件名,url路径存在数据库里面
            '''
            file_name = time.time() + audio.filename
            if write_audio_in_staticfile(file_name, audio):
                item.valid_time = request.form['valid_time']
                item.announce_type = 'audio'
                item.announce_content = file_name
                db.session.commit()
                return jsonify({'res_code': 200, 'res_msg': 'success'})
            else:
                return jsonify({'res_code': 400, 'res_msg': 'fail write file'})
        else:
            '''
            item未找到
            '''
            return jsonify({'res_code': 400, 'res_msg': 'no this item'})
    else:
        '''
        类型是文字类型
        '''
        item = db.session.query(announce).filter_by(user_id=userId).filter_by(id=announceId).first()
        if item:
            item.valid_time = request.form['valid_time']
            item.announce_type = 'text'
            item.announce_content = request.form['content']
            db.session.commit()
            return jsonify({'res_code': 200, 'res_msg': 'success'})
        else:
            return jsonify({'res_code': 400, 'res_msg': 'no this item'})


# completed
def write_audio_in_staticfile(file_name, content):
    '''
    把音频文件存储在指定目录下
    :param file_name: 音频文件名，时间戳和文件名结合
    :param content: 音频内容
    :return: 返回状态值
    '''
    try:
        static_path = os.path.join(os.path.abspath('..'), 'static', file_name)
        with open(static_path, 'wb') as target:
            target.write(content)
        return True
    except Exception:
        return False


# completed
@web.route('/addAnnounceById/<int:userId>', methods=['POST'])
def addAnnounceById(userId):
    '''
    添加账户的公告
    :param userId:使用者id
    :param annonce:公告数据，这里公告数据前端挥发一个值
    :return:状态值
    '''

    if request.files['announce_type'] == 'audio':
        audio = request.files['audio']
        new_announce = announce()
        new_announce.user_id = userId
        new_announce.valid_time = request.form['valid_time']
        new_announce.announce_type = request.form['announce_type']
        file_name = time.time() + audio.filename
        write_audio_in_staticfile(file_name, audio)
        new_announce.announce_content = file_name
        db.session.add(new_announce)
        db.session.commit()
        return jsonify({'res_code': 200, 'res_msg': 'success'})
    else:
        '''
        text情况
        '''
        new_announce = announce()
        new_announce.user_id = userId
        new_announce.valid_time = request.form['valid_time']
        new_announce.announce_type = request.form['announce_type']
        new_announce.announce_content = request.form['content']
        db.session.add(new_announce)
        db.session.commit()
        return jsonify({'res_code': 200, 'res_msg': 'success'})


# none
def is_announce_audio():
    pass


# tips
@web.route('/deleteAnnounceById/<int:userId>/<int:announceId>')
def deleteAnnounceById(userId, announceId):
    '''
    删除账户的指定公告,这个地方没有去删除对应文件，文件永远就留存在了服务器
    :param userId: 使用者id
    :param announceId: 公告id
    :return: 状态值
    '''

    item = db.session.query(announce).filter_by(user_id=userId).filter_by(
        id=announceId).first()
    if item:
        '''
        找到item删除掉
        '''
        db.session.delete(item)
        db.session.commit()
        return jsonify({'res_code': 200, 'res_msg': 'success'})
    else:
        return jsonify({'res_code': 400, 'res_msg': 'fail'})


# completed
@web.route('/searchAnnounceById/<int:userId>/<int:announceId>')
def searchAnnounceById(userId, announceId):
    '''
    搜索指定账户指定公告的数据
    :param userId: 使用者id
    :param announceId: 公告id
    :return: 公告数据
    '''
    announcement = db.session.query(announce).filter_by(user_id=userId).filter_by(id=announceId).first()
    if announcement:
        return jsonify({'id': announcement.id, 'user_id': announcement.user_id, 'valid_time': announcement.valid_time,
                        'announce_type': announcement.announce_type, 'announce_content': announcement.announce_content})
    else:
        return jsonify({'res_code': 200, 'res_msg': 'no this item'})


# completed
@web.route('/get_audit_AnnouncesById/<int:userId>')
def get_audit_AnnouncesById(userId):
    '''
    被添加id
    :param userId: 被添加使用者id
    :return: 状态值
    '''
    all_audits = db.session.query(audit_announce).filter_by(user_id_added=userId).all()
    if len(all_audits) > 0:
        '''
        查找到数组
        '''
        audits_list = []
        for audit in all_audits:
            key_list = ('user_id_add', 'valid_time', 'annouce_type', 'announce_content')
            value_list = (
                all_audits.user_id_add, all_audits.valid_time, all_audits.announce_type, all_audits.announce_content)
            new_audit = dict(zip(key_list, value_list))
            new_audit_jsonify = json.dumps(new_audit)
            audits_list.append(new_audit_jsonify)
        return jsonify(audits_list)
    else:
        '''
        没有查找到
        '''
        return jsonify([])


# complete
@web.route('/addAnnounceToFriend/<int:userId>/<int:targetId>', methods=['POST'])
def addAnnounceToFriend(userId, targetId):
    '''
    给目标id条审批公告
    :param userId: 当前用户id
    :param targetId: 目标用户id
    :param announce:公告数据（POST发送）
    :return: 状态值
    '''
    '''通过id吧事项发到事件确认列表'''
    if request.files['announce_type'] == 'audio':
        '''
        是音频输入
        '''
        new_audit_announce = audit_announce()
        new_audit_announce.user_id_added = targetId
        new_audit_announce.user_id_add = userId
        new_audit_announce.valid_time = request.form['valid_time']
        new_audit_announce.announce_type = 'audio'
        audio = request.files['audio']
        file_name = time.time() + audio.filename
        write_audio_in_staticfile(file_name, audio)
        new_audit_announce.announce_content = file_name
        db.session.add(new_audit_announce)
        db.session.commit()
        return jsonify({'res_code': 200, 'res_msg': 'success'})
    else:
        new_audit_announce = audit_announce()
        new_audit_announce.user_id_added = targetId
        new_audit_announce.user_id_add = userId
        new_audit_announce.valid_time = request.form['valid_time']
        new_audit_announce.announce_type = 'text'
        new_audit_announce.announce_content = request.form['content']
        db.session.add(new_audit_announce)
        db.session.commit()
        return jsonify({'res_code': 200, 'res_msg': 'success'})
    # new_audit_announce.valid_time =


# none
@web.route('/comfirmAnnounce/<int:announceId>')
def comfirm(announceId):
    '''
    审批通过某条数据
    :param announceId:数据id号
    :return: 状态值
    '''
    item = db.session.query(audit_announce).filter_by(id=announceId).first()
    if item:
        '''
        查找到对应id的announce
        '''
        new_announce = announce()
        new_announce.user_id = item.user_id_added
        new_announce.valid_time = item.valid_time
        new_announce.announce_type = item.announce_type
        new_announce.announce_content = item.announce_content
        return jsonify({'res_code': 200, 'res_msg': 'success'})
    else:
        return jsonify({'res_code': 400, 'res_msg': 'fail'})


# none
@web.route('/resistAnnounce/<int:announceId>')
def resist(announceId):
    '''
    拒绝某一条公告
    :param announceId:公告id
    :return: 状态值
    '''
    item = db.session.query(audit_announce).filter_by(id=announceId).first()
    if item:
        '''
        查找到对应id的announce
        '''
        db.session.delete(item)
        db.session.commit()
        return jsonify({'res_code': 200, 'res_msg': 'success'})
    else:
        return jsonify({'res_code': 400, 'res_msg': 'fail'})
