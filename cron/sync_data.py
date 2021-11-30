import os
import datetime
import logging
import requests
import threading
from functools import wraps
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(
    format='%(levelname)s:%(asctime)s %(pathname)s--%(funcName)s--line %(lineno)d-----%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
)


def func_log(func):
    '''
    log operation details
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):

        thread_id = threading.get_ident()
        start_time = datetime.datetime.now()
        logging.warning('[== %s ==]start func [ %s ]' % (thread_id, func.__name__))
        try:
            result = func(*args, **kwargs)
            logging.warning(result)
        except Exception as e:
            print(e)
            result = {"code": 99904, "msg": "system error"}
        end_time = datetime.datetime.now()
        cost_time = end_time - start_time
        logging.warning(
            '[== %s ==]func[ %s ] completed，used[ %s ]s' % (thread_id, func.__name__, cost_time.total_seconds()))

        return result

    return wrapper


@func_log
def add_notaries():
    url = os.getenv('SERVER_COMPANY') + '/company/api/partner/add_notaries'
    return requests.post(url=url, timeout=600, data={}).json()


@func_log
def get_req_record():
    """record datacap request"""
    url = os.getenv('SERVER_TOOLS') + '/tools/api/get_req_record'
    return requests.post(url=url, timeout=600, data={}).json()


@func_log
def get_msg_data():
    """get msg cid and details"""
    url = os.getenv('SERVER_TOOLS') + '/tools/api/get_msg_data'
    return requests.post(url=url, timeout=600, data={}).json()


@func_log
def get_deal_info():
    """get deal info"""
    url = os.getenv('SERVER_TOOLS') + '/tools/api/get_deal_info'
    return requests.post(url=url, timeout=600, data={}).json()


@func_log
def refresh_data():
    """refresh redis data"""
    url = os.getenv('SERVER_TOOLS') + '/tools/api/refresh_data'
    return requests.post(url=url, timeout=600, data={}).json()


@func_log
def get_address():
    """record github apply address"""
    url = os.getenv('SERVER_TOOLS') + '/tools/api/get_address'
    return requests.post(url=url, timeout=600, data={}).json()


@func_log
def check_closed_issue():
    """check if issues has closed"""
    url = os.getenv('SERVER_TOOLS') + '/tools/api/check_closed_issue'
    return requests.post(url=url, timeout=600, data={}).json()


if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")

    scheduler.add_job(func=add_notaries, trigger='interval', seconds=60 * 60)
    scheduler.add_job(func=get_req_record, trigger='cron', hour=0, minute=1)
    scheduler.add_job(func=get_msg_data, trigger='cron', hour=0, minute=30)
    scheduler.add_job(func=get_deal_info, trigger='cron', hour=1, minute=5)
    scheduler.add_job(func=refresh_data, trigger='cron', hour=2, minute=0)
    scheduler.add_job(func=get_address, trigger='cron', hour=0, minute=30)
    scheduler.add_job(func=check_closed_issue, trigger='cron', hour=0, minute=40)

    scheduler.start()
