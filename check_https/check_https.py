import os
import socket
import ssl
import datetime
import logging
import requests
from .models import domain, domain_https


logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(filename)s %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename=os.getenv("LOG_PATH",'ssl_check.log'),
    filemode='a')

logger = logging.getLogger('')


class AlreadyExpired(Exception):
    def __init__(self, message, errors):
        super(AlreadyExpired, self).__init__(message)
        self.errors = errors


def alert(message):
    print(message)
    requests.post("http://msg.ops.dragonest.com/notify/%s/send/" % os.getenv('MSG_NOTIFY_ID',"3"), data={"content": message}, headers={"Authorization": "Token %s" % os.getenv('MSG_TOKEN', "c25fa3f66b02c8b83cff9090125df91db288cecb") })

def ssl_expiry_datetime(hostname, port=443):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    # 60 second timeout
    conn.settimeout(60.0)

    conn.connect((hostname, port))
    ssl_info = conn.getpeercert()

    domain_name = hostname
    ca = ssl_info['issuer'][3][0][1]
    starttime = datetime.datetime.strptime(ssl_info['notBefore'], ssl_date_fmt)
    endtime = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)

    domain_https.objects.create(domain_https_name = domain_name, domain_https_ca = ca, domain_https_endtime = endtime, domain_https_starttime = starttime)

    return endtime

def ssl_valid_time_remaining(hostname, port=443):
    """Get the number of days left in a cert's lifetime."""
    expires = ssl_expiry_datetime(hostname, port)
    logger.debug(
        "SSL cert for %s expires at %s",
        hostname, expires.isoformat()
    )
    return expires - datetime.datetime.utcnow()


def check(hostname, port=443, buffer_days=14):
    """Check if `hostname` SSL cert expires is within `buffer_days`.
       return: alert_level, message

    """
    message = ""
    try:
        remaining = ssl_valid_time_remaining(hostname, int(port))
    except Exception as e:
        return 'error', "%s %s" % (hostname, str(e))

    if remaining < datetime.timedelta(days=0):
        return "fatal", "%s Cert expired %s days ago" % (hostname, remaining.days)
    elif remaining < datetime.timedelta(days=buffer_days):
        return 'warning', "%s Cert will be expired in %s days" % (hostname, remaining.days)
    else:
        return 'ok', 'everything is fine'

def check_https():
    import sys
    import os

    alert_data = {
        "warning": [],
        "error": [],
        "fatal": [],
    }


    alert_msg = ""
    do_alert = False

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE_DIR, 'hostname_list.txt'), 'r') as f:
        hostname_list = f.readlines()
    for hostname in hostname_list:
        if hostname:
            result, message = check(*hostname.strip().split(":"), buffer_days=14)
            if result in ["warning", "error", "fatal" ]:
                alert_data[result].append(message)
                if hostname.strip().split(":")[0] in ['account.dragonest.com', 'account.ilongyuan.cn']:
                    alert_data[result].append("%s 在海外有做智能DNS解析，请务必同时更新海外加速点slb的证书" % hostname)


    if alert_data['warning']:
        alert_msg = u"发现如下即将过期的域名，请尽快更新证书:\n------------\n%s\n\n" % "\n".join(alert_data['warning'])
        do_alert = True

    if alert_data['fatal']:
        alert_msg = u"%s发现如下证书已过期，请尽快处理:\n------------\n%s\n\n" % (alert_msg, "\n".join(alert_data['fatal']))
        do_alert = True

    if alert_data['error']:
        alert_msg = u"%s检查以下域名ssl证书时遇到错误，请手动确认:\n------------\n%s\n\n" % (alert_msg, "\n".join(alert_data['error']))
        do_alert = True

    if do_alert:
        alert(alert_msg)

