from django.contrib import admin
from .models import LoginToken


@admin.register(LoginToken)
class LoginTokenAdmin(admin.ModelAdmin):
    list_display  = ('user', 'token', 'expires_at', 'created_at')
    list_filter   = ('user',)
    search_fields = ('user__username', 'token')
    readonly_fields = ('token', 'created_at')

