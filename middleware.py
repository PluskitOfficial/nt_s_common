import time
import logging
from django.utils.deprecation import MiddlewareMixin


class ResponseMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):

        request.user_id = request.META.get("HTTP_USERID", "")
        request.app_id = request.META.get("HTTP_APPID", "")
        request.app_version = request.META.get("HTTP_APPVERSION", "")
        request.device_id = request.META.get("HTTP_DEVICEID", "")
        request.real_ip = request.META.get("HTTP_REAL_IP_FROM_API", "")
        # language
        request.lang = request.META.get('HTTP_LANG') or 'zh'
        # user_agent
        request.user_agent = request.META.get('HTTP_USER_AGENT', '')
        self.start_time = time.time()

    def process_response(self, request, response):
        end_time = time.time()
        t = end_time - self.start_time
        if t >= 5:
            logging.error("LONG_PROCESS:%s%s %ss" % (request.get_host(), request.get_full_path(), t))
        return response

    def process_exception(self, request, exception):
        from nt_s_common import debug

        detail = "post_data is:" + str(request.POST) + debug.get_debug_detail(exception)
        detail += ("user_id:%s, app_id:%s, app_version:%s, device_id:%s" % (request.user_id, request.app_id, request.app_version, request.device_id))
        url = request.get_full_path()
