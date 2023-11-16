class Base:
    def __init__(self):
        pass

    def check_args(self, args):
        raise NotImplementedError

    def cal(self):
        raise NotImplementedError

    def run(self, args):
        raise NotImplementedError
