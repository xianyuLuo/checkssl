FROM i.harbor.dragonest.net/public/python:3.6
COPY . /check_ssl
RUN pip3 install --trusted-host mirrors.aliyun.com -i http://mirrors.aliyun.com/pypi/simple -r /check_ssl/requirements.txt && \
  chmod +x /check_ssl/entrypoint.sh
USER root
WORKDIR /check_ssl