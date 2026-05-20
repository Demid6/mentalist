from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Comment


@admin.register(User)
class AgentAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('phone',)}),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'text', 'created_at')
    list_filter = ('created_at',)
