from django.contrib import admin
from ecapp.models import Contact, Product, Orders, OrderUpdate

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phonenumber')
    search_fields = ('name', 'email', 'phonenumber')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price')
    search_fields = ('product_name', 'category')
    list_filter = ('category', 'subcategory')
    ordering = ('-price',)

class OrdersAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'name', 'amount', 'paymentstatus', 'city')
    search_fields = ('name', 'email', 'order_id')
    list_filter = ('paymentstatus', 'city', 'state')
    ordering = ('-order_id',)
    
class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ('update_id', 'order_id', 'delivered', 'timestamp')
    search_fields = ('order_id',)
    list_filter = ('delivered', 'timestamp')

admin.site.register(Contact, ContactAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(OrderUpdate, OrderUpdateAdmin)
