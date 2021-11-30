from functools import wraps
from django.http import HttpResponse, JsonResponse
from nt_s_common import cache, debug
from nt_s_common.utils import format_return


def common_ajax_response(func):
    """
    @note: format return value，e.g.：dict(code=0, msg='', data={})
    """

    def _decorator(request, *args, **kwargs):
        result = func(request, *args, **kwargs)
        if isinstance(result, HttpResponse):
            return result
        code, msg, data = result

        r = dict(code=code, msg=msg, data=data)
        response = JsonResponse(r)
        return response

    return _decorator


def validate_params(func):
    """
    @note: validate decorator
    """

    def _decorator(*args, **kwargs):

        def _get_param_items(func, args, kwargs):
            import inspect
            parameters = inspect.signature(func).parameters
            arg_keys = tuple(parameters.keys())
            vparams = [k for k, v in parameters.items() if k == str(v)]

            param_items = []
            # collect args   *args
            for i, value in enumerate(args):
                _key = arg_keys[i]
                if _key in vparams:
                    param_items.append([_key, value])

            # collect kwargs  **kwargs
            for arg_name, value in kwargs.items():
                if arg_name in vparams:
                    param_items.append([arg_name, value])

            return param_items

        check_list = _get_param_items(func, args, kwargs)
        # cannot be null
        for item in check_list:
            if item[1] is None:
                return format_return(99901)

        return func(*args, **kwargs)

    return _decorator


def cache_required(cache_key, cache_key_type=0, expire=3600 * 24, cache_config=cache.CACHE_TMP):
    """
    @note: cache decorator
    cache_key format：1：'answer_summary_%s' as changeable key  2：'global_var' as fixed value
    if cache_key should be formatted，use cache_key_type：
    0：param：func(self, cache_key_param)，取cache_key_param或者cache_key_param.id
    1：param：func(cache_key_param)
    2：param：func(self) cache_key为self.id
    """

    def _wrap_decorator(func):

        func.cache_key = cache_key

        def _decorator(*args, **kwargs):
            cache_key = func.cache_key
            must_update_cache = kwargs.get('must_update_cache')

            if '%' in cache_key:
                assert len(args) > 0
                if cache_key_type == 0:
                    key = args[1].id if hasattr(args[1], 'id') else args[1]
                    if isinstance(key, (str, int, float)):
                        cache_key = cache_key % key
                    else:
                        return
                if cache_key_type == 1:
                    cache_key = cache_key % args[0]
                if cache_key_type == 2:
                    cache_key = cache_key % args[0].id
            return cache.get_or_update_data_from_cache(cache_key, expire, cache_config,
                                                       must_update_cache, func, *args, **kwargs)

        return _decorator

    return _wrap_decorator


def one_by_one_locked(func):
    """
    @note: thread lock, avoid  Concurrency problems
    """

    def _decorator(*args, **kwargs):
        import time
        import uuid

        cache_obj = cache.Cache()
        cache_key_suffix = ""
        cache_key = None
        if len(args) > 1:
            # the cache key is the first param
            cache_key_suffix = args[1]
        else:
            if kwargs:
                # or the cache key is the val of cahce_key
                if kwargs.get('cache_key'):
                    cache_key = "%s_%s" % ('one_by_one_locker', kwargs.get('cache_key'))
                cache_key_suffix = list(kwargs.items())[0][1]
        if not cache_key:
            cache_key = "%s_%s" % (func.__name__, cache_key_suffix)  # cache key

        uuid_str = str(uuid.uuid4())

        flag = None

        while not flag:
            flag = cache_obj.set_lock(cache_key, uuid_str, ex=5, nx=True)  # add lock
            if not flag:
                time.sleep(0.002)
        r = func(*args, **kwargs)
        if cache_obj.get(cache_key) == uuid_str:
            cache_obj.delete(cache_key)  # delete lock after handling
        return r

    return _decorator


def lang_translate(func):
    """
    lang decorator

    @lang_translate
    def delete(request):
        pass

    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):

        result = list(func(request, *args, **kwargs))
        from nt_s_common.consts import ERROR_DICT
        # template
        lang_msg = ERROR_DICT.get(request.lang, {}).get(result[0], result[1])
        default_msg = ERROR_DICT.get('zh', {}).get(result[0])

        # the return data contains the template or not
        if lang_msg.find('%s') > -1:
            result[1] = lang_msg % (result[1])
        else:
            result[1] = result[1] if result[1] != default_msg else lang_msg

        return result

    return wrapper
