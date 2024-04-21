from django.contrib import admin
from django.urls import path
from .views import *
from base.helpers import *
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',index,name='index'),
    path('product_details/<slug:slug>/',get_product,name='get_product'),
    path('add_to_cart/<uid>/', add_to_cart, name='add_to_cart'),
    path('wish_list/<uid>/', wishlist, name='wish_list'),
    path('remove_wishlist/<uuid:wishlist_uid>/', remove_wishlist, name='remove_wishlist'),
    path('wishlist_view/',wishlist_view,name='wishlist_view'),
    path('buy_now/<uid>/', buy_now, name='buy_now'),
    path('cart/',cart,name='cart'),
    path('remove_cart/<uuid:cart_item_uid>/', remove_cart, name='remove_cart'),
    #path('update_quantity/', update_quantity, name='update_quantity'),
    path('increase_quantity/<uuid:cart_item_uid>/', increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<uuid:cart_item_uid>/', decrease_quantity, name='decrease_quantity'),
    path('remove_coupon/<uuid:cart_uid>/',remove_coupon,name='remove_coupon'),
    path('success/',success_razorpay,name='success'),
    path('checkout/',checkout_page,name='checkout'),
    #path('process_payment/', payment_option, name='process_payment'),
    path('payment_option/', payment_option, name='payment_option'),
   # path('payment_cod/', payment_cod, name='payment_cod'),
    path('success_cod/',success_cod,name='success_cod'),
    #path('invoice/<uuid:cart_uid>/', invoice_pdf, name='invoice_pdf'),
    path('download-pdf/<str:file_name>/', download_pdf, name='download_pdf'),
    path('profile/', profile, name='profile'),
    path('profile_edit/<user_id>/', profile_edit, name='profile_edit'),
    path('orderlist/',order_list, name='orderlist'),
    path('order_details/<uuid:order_id>/', order_details, name='order_details'),

    path('order_return/<uuid:cart_uid>/', order_return, name='order_return'),
    path('order_cancel/<uuid:cart_uid>/', order_cancel, name = 'order_cancel'),
    path('order_return_tracker/<uuid:order_id>/', order_return_tracker, name='order_return_tracker'),
    path('contactus/', contactus, name='contactus'),
    #path('get_available_sizes/', views.get_available_sizes, name='get_available_sizes'),
    #path('email/<uuid:cart_uid>/', email_order_confirmation, name='email'),
    path('search/', search, name='search_results'),

    



]