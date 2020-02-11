from django.contrib import admin

from .models import Item, Account, Transaction, Property, Application


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    exclude = ('access_token',)


admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Property)
admin.site.register(Application)
 