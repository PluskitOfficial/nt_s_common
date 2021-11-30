import re
import json
import time
import random
import datetime
import decimal

from nt_s_common.consts import ERROR_DICT


def format_return(code, msg='', data=None, change_none=False, lang='zh'):
    temp = data if data != None else {}

    if change_none:
        temp = json.loads(json.dumps(temp).replace('null', '""'))
    return code, msg or ERROR_DICT.get(lang, {}).get(code, ''), temp


def format_number(number):
    return number.quantize(decimal.Decimal('0.00')) if number is not None else ""


def get_ip(request):
    if 'HTTP_REAL_IP_FROM_API' in request.META:
        return request.META['HTTP_REAL_IP_FROM_API']
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        client_ip = request.META['HTTP_X_FORWARDED_FOR']
        arr_ip = client_ip.split(',', 1)
        return arr_ip[0].strip()
    elif 'HTTP_X_REAL_IP' in request.META:
        return request.META['HTTP_X_REAL_IP']
    else:
        return request.META.get('REMOTE_ADDR', '127.0.0.1')


def format_price(price, point=2):
    return ('%.' + str(point) + 'f') % decimal.Decimal(price) if price is not None else ''


def format_power(power, unit='DiB'):
    units = ["KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB", "BiB", "NiB", "DiB"]
    unit_index = 0

    power = decimal.Decimal(power)
    _power = abs(power)
    temp = _power / 1024
    while (temp >= 1024) and (unit_index <= len(units)):
        unit_index += 1
        temp = temp / 1024
        if units[unit_index] == unit:
            break

    return '%s%s %s' % ('-' if power < 0 else '', format_price(temp), units[unit_index])


def format_power_to_TiB(power):
    units = ["KiB", "MiB", "GiB", "TiB"]
    unit_index = 0

    power = decimal.Decimal(power)
    temp = power / 1024
    while (temp > 1024) and (unit_index < len(units) - 1):
        unit_index += 1
        temp = temp / 1024

    return '%s %s' % (format_price(temp), units[unit_index])


def str_2_power(power_str):
    if power_str == "" or power_str is None:
        return power_str
    mapping = {
        'NiB': 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024,
        'YiB': 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024,
        'ZiB': 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024,
        'EiB': 1024 * 1024 * 1024 * 1024 * 1024 * 1024,
        'PiB': 1024 * 1024 * 1024 * 1024 * 1024,
        'TiB': 1024 * 1024 * 1024 * 1024,
        'GiB': 1024 * 1024 * 1024,
        'MiB': 1024 * 1024,
        'KiB': 1024
    }

    value, unit = power_str.split(' ')
    return int(float(value) * mapping.get(unit, 1))


def _d(v):
    return decimal.Decimal(v)
