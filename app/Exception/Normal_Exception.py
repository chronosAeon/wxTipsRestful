class Normal_Exception(Exception):
    def __init__(self, res_code, res_msg, error_msg='基础异常'):
        super(Normal_Exception, self).__init__(error_msg)
        self.res_code = res_code
        self.res_msg = res_msg

    def get_back_msg(self):
        '''
        构造基本的异常返回的dict
        :return: 返回异常信息dict
        '''
        res_dict = {'res_code': self.res_code, 'res_msg': self.res_msg}
        return res_dict
