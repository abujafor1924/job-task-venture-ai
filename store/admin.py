from django.contrib import admin
from store.models import Product,Category,Size,Color,Specification,Gallery,Cart,CartOrder,CartOrderItem

# Register your models here.

class GelleryInline(admin.TabularInline):
     model=Gallery

class SpecificationInline(admin.TabularInline):
     model=Specification

class SizeInline(admin.TabularInline):
     model=Size

class ColorInline(admin.TabularInline):
     model=Color
class ProductAdmin(admin.ModelAdmin):
     list_display=['title','price','old_price','shipping_amount','stock_qty','inStock','status','views','rating','pid','featured']
     list_editable=['featured']
     list_filter=['date']
     search_fields=['title','pid']
     inlines=[GelleryInline,SpecificationInline,SizeInline,ColorInline]
     
class CartOrderAdmin(admin.ModelAdmin):
     list_display=['oid','total','buyer','payment_Status','order_status']
     

admin.site.register(Category)
admin.site.register(Product,ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartOrder,CartOrderAdmin)
admin.site.register(CartOrderItem)

