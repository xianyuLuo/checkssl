from django.db import models

# 域名模型
class domain(models.Model):
    domain_name = models.CharField('域名', max_length = 50, help_text = "业务域名")
    domain_port = models.IntegerField('端口', default = 443, help_text = "端口")
    domain_overseas = models.BooleanField('是否有海外HTTPS', default = False, help_text = "是否有海外https")
    domain_comment = models.TextField('备注', max_length = 500, blank = True, help_text = "备注")

    def __str__(self):
        return self.domain_name

    class Meta:
        verbose_name = "域名"
        verbose_name_plural = verbose_name

# 域名https检查模型
class domain_https(models.Model):
    domain_https_name = models.CharField('域名', max_length = 50, help_text = "业务域名")
    domain_https_ca = models.CharField('CA中心', max_length = 50, help_text = "域名CA")
    domain_https_starttime = models.CharField('申请时间', max_length = 50, help_text = "域名证书申请时间")
    domain_https_endtime = models.CharField('到期时间', max_length = 50, help_text = "域名证书到期时间")
    domain_https_chrome = models.BooleanField('证书是否被Chrome信任', max_length = 10, default = True, help_text = "域名证书是否被Chrome信任")

    def __str__(self):
        return self.domain_https_name

    class Meta:
        verbose_name = "证书信息"
        verbose_name_plural = verbose_name