import logging
from os.path import normpath, join, split
from os import getenv


class ElLogger(object):
    def __init__(self, name=None, file=None, level=10):
        super(ElLogger, self).__init__()
        self.name = name
        self.file = file
        self.log = None
        if name:
            self.set_name(name)
            self.set_level(level)
        if file:
            self.set_log_file(self.file)

    def set_name(self, name):
        self.name = name
        self.log = logging.getLogger(name)

    def set_level(self, level):
        """level: DEBUG 10; ERROR 40"""
        self.log.setLevel(level)

    def set_log_file(self, file=None):
        if file:
            self.file = file
        else:
            # _pth, name = split(getenv('userprofile'))
            self.file = normpath(join(getenv('userprofile'), 'Documents', 'log_{}.txt'.format(self.name)))
        print('Log file: %s' % self.file)
        fh = logging.FileHandler(self.file, mode='w', encoding='utf-8')
        # x = u'%(levelname)-8s | %(lineno)-3d | %(module)-18s | %(funcName)s | [%(asctime)s] | %(message)s'
        x = '----' * 20
        # 'debug'
        # 'error'
        # 'warning'
        x += u'\n%(levelname)-8s| %(funcName)-26s | %(asctime)s\n  %(lineno)-5d : %(message)s '
        # x += u"\n  %(lineno)-5d : %(message)s"
        formatter = logging.Formatter(x)
        fh.setFormatter(formatter)
        self.log.addHandler(fh)

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

    def close(self):
        handlers = self.log.handlers[:]
        for h in handlers:
            h.close()
            self.log.removeHandler(h)


