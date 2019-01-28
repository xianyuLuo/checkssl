# Check_ssl

用于检查域名https证书过期时间

# 所需环境变量
- LOG_PATH：日志路径配置，/dev/stdout
- MSG_NOTIFY_ID：send_msg配置
- MSG_TOKEN： send_msg配置
- CELERY_BROKER_URL：redis或者rab地址

# 启动
- http启动
python manage.py migrate
python manage.py runserver

- celery worker启动：
celery -A check_ssl worker  -l info -P solo

- celery beta启动：
celery -A check_ssl beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler