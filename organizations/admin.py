from django.contrib import admin
from .models import NKO, NKOMembership


# Register your models here.
@admin.register(NKO)
class NKOAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'category', 'status', 'owner', 'created_at']
    list_filter = ['status', 'category', 'city', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_nko', 'reject_nko']

    def approve_nko(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, "НКО одобрены")

    approve_nko.short_description = "Одобрить выбранные НКО"

    def reject_nko(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "НКО отклонены")

    reject_nko.short_description = "Отклонить выбранные НКО"


@admin.register(NKOMembership)
class NKOMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'nko', 'role', 'status', 'joined_at']
    list_filter = ['status', 'role', 'joined_at']
    search_fields = ['user__username', 'nko__name']
    readonly_fields = ['joined_at']
