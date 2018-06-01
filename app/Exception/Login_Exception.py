from app.Exception.Normal_Exception import Normal_Exception


class Login_Exception(Normal_Exception):
    def __init__(self, res_code, res_msg, error_msg='登陆异常'):
        super(Login_Exception, self).__init__(res_code, res_msg, error_msg)
