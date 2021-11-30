import os

# error dict
ERROR_DICT = {
    'zh': {
        0: '成功',
        99901: '参数缺失',
        99902: '参数异常',
        99903: '参数重复',
        99904: '系统错误',
    },
    'en': {
        0: 'success',
        99901: 'parameter miss',
        99902: 'parameter error',
        99903: 'parameter repeat',
        99904: 'system error',
    }
}

# 微服务地址
SERVER_TOOLS = os.getenv('SERVER_TOOLS')

# xm项目配置
XM_HOST = os.getenv('XM_HOST')
XM_APP_ID = os.getenv('XM_APP_ID')
XM_APP_SECRET = os.getenv('XM_APP_SECRET')
