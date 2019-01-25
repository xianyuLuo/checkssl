from django.contrib import admin, messages
from .models import domain, domain_https
from .check_ssl_expiration import check, update_https_info
# Register your models here.

class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain_name', 'domain_port', 'domain_comment']
    list_filter = ['domain_name']
    search_fields = ['domain_name']
    list_per_page = 40
    actions = ["update"]

    def update(self, request, queryset):
        # queryset.update(domain_port = 443)
        # msg = "更新已完成"
        # self.message_user(request, msg, messages.SUCCESS)
        update_https_info()
        check()

    update.short_description = "https证书检查"

class DomainHttpsAdmin(admin.ModelAdmin):
    list_display = ['domain_https_name', 'domain_https_ca', 'domain_https_starttime', 'domain_https_endtime', 'domain_https_chrome']
    list_filter = ['domain_https_name', 'domain_https_ca']
    search_fields = ['domain_https_name']
    list_per_page = 20

admin.site.register(domain, DomainAdmin)
admin.site.register(domain_https, DomainHttpsAdmin)