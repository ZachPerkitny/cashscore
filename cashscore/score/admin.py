from django.contrib import admin

from .models import Item, Account, Transaction, Property, Application


admin.site.register(Item)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Property)
admin.site.register(Application)
 