import uuid


class Token_generator:
    def generate_token(self):
        '''
        基于伪随机的code，会有极小概率重复
        :return: code
        '''
        return uuid.uuid4().hex


if __name__ == "__main__":
    print(uuid.uuid4().hex)
