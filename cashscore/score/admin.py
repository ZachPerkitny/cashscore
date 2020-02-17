from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Item, Account, Transaction, Property, Application


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    exclude = ('access_token',)
    list_display = ('id', 'institution_name', 'last_pull',)
    readonly_fields = ('institution_name',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'subtype',)
    list_filter = ('type', 'subtype',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'transaction_type', 'account_link',)
    list_filter = ('transaction_type',)
    search_fields = ('transaction_type',)

    def account_link(self, obj):
        link = reverse('admin:score_account_change', args=[obj.account.id])
        return format_html('<a href="{}">View {} Account</a>', link, obj.name)

    account_link.short_description = 'View Account'


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'address',)
    search_fields = ('address',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_property', 'unit', 'rent_asked',
        'applicant_name', 'applicant_email', 'is_completed',)

    def is_completed(self, instance):
        return instance.is_completed

    is_completed.boolean = True
