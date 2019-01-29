from django.contrib import admin, messages
from .models import domain, domain_https
from .tasks import CheckHttpsInfo, UpdateHttpsInfo

class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain_name', 'domain_port', 'domain_comment']
    list_filter = ['domain_name']
    search_fields = ['domain_name']
    list_per_page = 50
    actions = ["update"]

    def update(self, request, queryset):
        # 异步执行任务
        handle_result = CheckHttpsInfo.delay()
        if handle_result:
            msg = "已下发到异步任务队列，请在日志中查看执行情况!!"
            self.message_user(request, msg, messages.SUCCESS)

    update.short_description = "https证书检查"

class DomainHttpsAdmin(admin.ModelAdmin):
    list_display = ['domain_https_name', 'domain_https_ca', 'domain_https_starttime', 'domain_https_endtime', 'domain_https_chrome']
    list_filter = ['domain_https_name', 'domain_https_ca']
    search_fields = ['domain_https_name']
    list_per_page = 50

admin.site.register(domain, DomainAdmin)
admin.site.register(domain_https, DomainHttpsAdmin)