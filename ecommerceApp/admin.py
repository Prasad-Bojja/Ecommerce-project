from django.contrib import admin
from .models import *

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

class CartItemInline(admin.StackedInline):
    model = CartItems

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name']
    prepopulated_fields = {'slug': ('category_name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'material','brand','price', 'product_description']
    inlines = [ProductImageAdmin]

@admin.register(ColorVariant)
class ColorAdmin(admin.ModelAdmin):
    list_display=['color_name','price']

@admin.register(SizeVariant)
class SizeAdmin(admin.ModelAdmin):
    list_display=['color_variant','size_name','price']

@admin.register(CODTransaction)
class CODTransactionAdmin(admin.ModelAdmin):
    list_display = ['cart','order_id', 'amount', 'transaction_date']

@admin.register(RazorpayTransaction)
class RazorpayTransactionAdmin(admin.ModelAdmin):
    list_display = ['cart','razor_pay_order_id', 'transaction_date','amount','is_paid']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'order_id','payment_methods', 'total_price','is_paid','status','delivery_date','notes']
    inlines = [CartItemInline]


@admin.register(CartItems)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user','cart', 'product', 'color_variant', 'size_variant', 'quantity', 'get_subtotal']
    
    def get_subtotal(self, obj):
        return obj.get_total_price()
    get_subtotal.short_description = 'Subtotal'

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['coupon_code', 'is_expired', 'discount_price', 'minimum_amount']

@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ['checkout','user','first_name', 'last_name', 'email', 'mobile','address1','address2','city','state','country','postal_code']

@admin.register(Wishlist)
class AdminWishList(admin.ModelAdmin):
    list_display=['user','product']


@admin.register(OrderCancel)
class AdminOrderCancel(admin.ModelAdmin):
    list_display = ['user','cart', 'cancellation_reason', 'cancellation_date']


@admin.register(ReturnStatus)
class AdminReturnStatus(admin.ModelAdmin):
    list_display = ['user','cart', 'return_reason','status', 'return_date' ,'notes']


@admin.register(ContactUs)
class AdminContactUs(admin.ModelAdmin):
    list_display = ['name', 'email', 'message']


