import json
import random
import time
import datetime
import hashlib
import requests
from urllib import parse

from nt_s_common import debug, utils, consts, decorator


class XmBase(object):

    def __init__(self):
        self.host = consts.XM_HOST
        self.app_id = consts.XM_APP_ID
        self.app_version = '1.0.0'
        self.app_secret = consts.XM_APP_SECRET

    def getSignature(self):
        '''get signature'''
        nonce = str(random.randint(1000000000, 9999999999))
        timestamp = str(int(datetime.datetime.timestamp(datetime.datetime.now())))
        params = sorted([nonce, timestamp, self.app_secret])
        sorted_params_str = ''.join(params)

        # calculate signature
        sha1 = hashlib.sha1()
        sha1.update(sorted_params_str.encode())
        sign = sha1.hexdigest()

        return 'signature=%s&timestamp=%s&nonce=%s' % (sign, timestamp, nonce)

    def getHeaders(self):
        '''set headers'''
        return {
            'AppId': self.app_id,
            'AppVersion': self.app_version,
            'Signature': self.getSignature(),
            'Content-type': 'application/x-www-form-urlencoded'
        }

    def fetch(self, url, data, timeout=60, repeat_time=3):
        for i in range(repeat_time):
            try:
                print('request url -------------------------->', url)
                print('post data -->', data)
                result = requests.post(url, headers=self.getHeaders(), data=data, timeout=timeout).json()
                print('response data -->', result)
                return result
            except Exception as e:
                print(e)
                if i >= repeat_time - 1:
                    return {}
                else:
                    continue

    def get_deal_list(self, data={}):
        """get deals """
        url = self.host + '/explorer_v2/block_chain/get_deal_list'
        return self.fetch(url=url, data=data, timeout=30)

    def get_message_list(self, data={}):
        """get msg list"""
        url = self.host + '/explorer_v2/block_chain/get_message_list'
        return self.fetch(url=url, data=data, timeout=30)

    def get_message_info(self, data={}):
        """get msg details"""
        url = self.host + '/explorer_v2/block_chain/get_message_info'
        return self.fetch(url=url, data=data, timeout=30)
