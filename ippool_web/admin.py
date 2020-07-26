from django.contrib import admin
from .models import cmdb, hardware_template


class CmdbAdmin(admin.ModelAdmin):
    list_display = ('ip', 'hostname', 'is_got_ip', 'is_set_vlan', 'dc', 'env', 'dept', 'type')
    search_fields = ('ip', 'is_got_ip', 'is_set_vlan', 'dc', 'env', 'dept', 'type')


class Template(admin.ModelAdmin):
    list_display = ('template', 'cpu', 'memory', 'capacity')


# Register your models here.
admin.site.register(cmdb, CmdbAdmin)
admin.site.register(hardware_template)
