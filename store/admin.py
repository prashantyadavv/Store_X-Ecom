from django.contrib import admin
from .models import Product, Category, Order, OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
