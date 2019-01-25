import os
import socket
import ssl
import datetime
import logging
import requests
from check_https.models import domain, domain_https


logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(filename)s %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename=os.getenv("LOG_PATH",'ssl_check.log'),
    filemode='a')

logger = logging.getLogger('')
buffer_days = 140

def alert(message):
    print(message)
    requests.post("http://msg.ops.dragonest.com/notify/%s/send/" % os.getenv('MSG_NOTIFY_ID',"19"), data={"content": message}, headers={"Authorization": "Token %s" % os.getenv('MSG_TOKEN', "c25fa3f66b02c8b83cff9090125df91db288cecb") })

# 更新所有域名信息到https列表
def update_https_info():
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

    for e in domain.objects.all():
        hostname = e.domain_name
        port = e.domain_port

        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=hostname,
        )
        conn.settimeout(60.0)
        conn.connect((hostname, port))
        ssl_info = conn.getpeercert()

        domain_name = hostname
        ca = ssl_info['issuer'][1][0][1]
        starttime = datetime.datetime.strptime(ssl_info['notBefore'], ssl_date_fmt)
        endtime = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)

        domain_https.objects.get_or_create(domain_https_name = domain_name, domain_https_ca = ca, domain_https_starttime = starttime, domain_https_endtime = endtime)

# 查看https列表中的信息
def check_https_info(hostname):
    ssl_date_fmt = r'%Y-%m-%d %H:%M:%S'
    if domain.objects.filter(domain_name = hostname)[0].domain_overseas:
        https_msg = "在海外有做智能DNS解析，请务必同时更新海外加速点slb的证书"
    else:
        https_msg = ""

    domain_https_endtime = datetime.datetime.strptime(domain_https.objects.filter(domain_https_name = hostname)[0].domain_https_endtime, ssl_date_fmt)
    print(domain_https_endtime)

    try:
        remaining = domain_https_endtime - datetime.datetime.utcnow()
    except Exception as e:
        return 'error', "%s %s" % (hostname, str(e))

    if remaining < datetime.timedelta(days=0):
        return "fatal", "%s Cert expired %s days ago %s" % (hostname, remaining.days, https_msg)
    elif remaining < datetime.timedelta(days=buffer_days):
        return 'warning', "%s Cert will be expired in %s days %s" % (hostname, remaining.days, https_msg)
    else:
        return 'ok', 'everything is fine'


def check():

    alert_data = {
        "warning": [],
        "error": [],
        "fatal": [],
    }

    alert_msg = ""
    do_alert = False

    hostname_list = list(domain.objects.values_list('domain_name'))
    for hostname in hostname_list:
        if hostname:
            result, message = check_https_info(hostname[0])
            if result in ["warning", "error", "fatal" ]:
                alert_data[result].append(message)

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

update_https_info()
check()