import logging
import re
import sys
import os
from logging.handlers import BaseRotatingHandler

LOG_FORMAT  = '%(thread)d %(threadName)s %(asctime)s %(filename)s %(funcName)s [line:%(lineno)d] %(levelname)s %(message)s'
LOG_LEVEL   = logging.DEBUG

# ��д RotatingFileHandler �Զ���log���ļ���
# ԭ�� xxx.log xxx.log.1 xxx.log.2 xxx.log.3 �ļ��ɽ���Զ
# ���� xxx.log xxx1.log xxx2.log  ���backupCount ��2λ��ʱ  �� 01  02  03 ��λ�� 001 002 .. �ļ��ɽ���Զ
class RotatingFileHandler(BaseRotatingHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        # if maxBytes > 0:
        #    mode = 'a'
        BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.placeholder = str(len(str(backupCount)))

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = ('%0'+ self.placeholder + 'd.')%i #  '%2d.'%i -> 02
                sfn = sfn.join(self.baseFilename.split('.'))
                # sfn = "%d_%s" % (i, self.baseFilename)
                # dfn = "%d_%s" % (i + 1, self.baseFilename)
                dfn = ('%0'+ self.placeholder + 'd.')%(i + 1)
                dfn = dfn.join(self.baseFilename.split('.'))
                if os.path.exists(sfn):
                    #print "%s -> %s" % (sfn, dfn)
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = (('%0'+ self.placeholder + 'd.')%1).join(self.baseFilename.split('.'))
            if os.path.exists(dfn):
                os.remove(dfn)
            # Issue 18940: A file may not have been created if delay is True.
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record):

        if self.stream is None:                 # delay was set...
            self.stream = self._open()
        if self.maxBytes > 0:                   # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        return 0

def get_logger(name = 'log.log', path = ''):
    logger = logging.getLogger(name)
    filename = path + name

    if not os.path.exists(path):
        os.makedirs(path)

    # ����
    logging.basicConfig(
            level=LOG_LEVEL,
            format= LOG_FORMAT,
            datefmt='%Y-%m-%d %H:%M:%S',
            )

    # #����һ��RotatingFileHandler����౸��5����־�ļ���ÿ����־�ļ����10M
    # Rthandler = RotatingFileHandler(filename, mode = 'w',  maxBytes=10 * 1024 * 1024,backupCount=20, encoding='utf8')
    # Rthandler.setLevel(LOG_LEVEL)
    # formatter = logging.Formatter(LOG_FORMAT)
    # Rthandler.setFormatter(formatter)

    # logger.addHandler(Rthandler)

    return logger

# logging.disable(logging.DEBUG) # �ر�����log

# ���� requests��ӡdebug��־ ������
# ���ô�ӡlog������
STOP_LOGS = [
    # ES
    'urllib3.response',
    'urllib3.connection',
    'elasticsearch.trace',
    'requests.packages.urllib3.util',
    'requests.packages.urllib3.util.retry',
    'urllib3.util',
    'requests.packages.urllib3.response',
    'requests.packages.urllib3.contrib.pyopenssl',
    'requests.packages',
    'urllib3.util.retry',
    'requests.packages.urllib3.contrib',
    'requests.packages.urllib3.connectionpool',
    'requests.packages.urllib3.poolmanager',
    'urllib3.connectionpool',
    'requests.packages.urllib3.connection',
    'elasticsearch',
    'log_request_fail',

    # requests
    'requests',
    'selenium.webdriver.remote.remote_connection',
    'selenium.webdriver.remote',
    'selenium.webdriver',
    'selenium',

    # markdown
    'MARKDOWN',
    'build_extension',

    # newspaper
    'calculate_area',
    'largest_image_url',
    'newspaper.images',
    'newspaper',
    'Importing',
    'PIL'
]

# �ر���־��ӡ
for STOP_LOG in STOP_LOGS:
    logging.getLogger(STOP_LOG).setLevel(logging.ERROR)
# print(logging.Logger.manager.loggerDict) # ȡʹ��debugģ���name

#��־�����С��ϵΪ��critical > error > warning > info > debug
PROJECT_NAME = ''.join(re.compile('.+\\\\(.+)').findall(sys.path[1]))

CURRENT_PATH = os.getcwd()
PROJECT_PATH = CURRENT_PATH[:CURRENT_PATH.find(PROJECT_NAME) + len(PROJECT_NAME)]
log= get_logger(PROJECT_NAME + '.log', PROJECT_PATH + '\\log\\')
