# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .check_ssl_expiration import update_https_info, check


@shared_task(bind = True)
def UpdateHttpsInfo(self):
    """
    更新域名证书信息
    """
    result = update_https_info()
    return_data = '[check_https.tasks.UpdateHttpsInfo], return result: {}'.format(result)
    return return_data

@shared_task(bind = True)
def CheckHttpsInfo(self):
    """
    检查https证书是否过期
    :param self:
    :return:
    """
    return check()

    # result = check()
    # return_data = '[check_https.tasks.CheckHttpsInfo], return result: {}'.format(result)
    # return return_data