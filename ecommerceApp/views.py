from collections import UserDict
from venv import logger
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, Http404
from .models import*
from authentications.models import *
from django.urls import reverse
from base.models import*
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import razorpay
from django.conf import settings
from django.db import transaction
from razorpay.errors import BadRequestError, ServerError
from django.core.exceptions import ObjectDoesNotExist
from base.helpers import*
from datetime import timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Q  

def index(request):
    categories = Category.objects.all()
    categorized_products = {}

    for category in categories:
        products = category.products.all()
        paginator = Paginator(products, 16)  
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        categorized_products[category.category_name] = page_obj

    
    context = {'categorized_products': categorized_products}
    return render(request, 'product_list.html', context)


def search(request):
    search_query = request.GET.get('search')
    search_results = []

    if search_query:
        search_results = Product.objects.filter(
            Q(product_name__icontains=search_query) |
            Q(product_description__icontains=search_query)
        )
        paginator = Paginator(search_results, 16)
        page_number = request.GET.get("page", 1)
        search_results = paginator.get_page(page_number)

    else:
        search_results = Product.objects.all()
        paginator = Paginator(search_results, 16)
        page_number = request.GET.get("page", 1)
        search_results = paginator.get_page(page_number)


    

    context = {'search_results': search_results, 'search_query': search_query}
    return render(request, 'base.html', context)


def get_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        context = {'product': product}

        if 'size' in request.GET and 'color' in request.GET:
            size = request.GET['size']
            color = request.GET['color']
            size_price = product.get_product_price_by_size(size)
            color_price = product.get_product_price_by_color(color)
            size_price = size_price or Decimal('0.0')
            color_price = color_price or Decimal('0.0')
            total_price = product.price + size_price + color_price
            product_price = product.price

            context['selected_size'] = size
            context['selected_color'] = color
            context['total_price'] = product_price
            context['updated_price'] = total_price
            available_sizes = product.available_sizes_for_color(color)
            context['available_sizes'] = available_sizes


        elif 'size' in request.GET:
            size = request.GET['size']
            size_price = product.get_product_price_by_size(size)
            # Ensure size_price is not None
            size_price = size_price or Decimal('0.0')
            total_price = product.price + size_price
            product_price = product.price
            context['selected_size'] = size
            context['total_price'] = product_price
            context['updated_price'] = total_price

        elif 'color' in request.GET:
            color = request.GET['color']
            color_price = product.get_product_price_by_color(color)
            # Ensure color_price is not None
            color_price = color_price or Decimal('0.0')
            total_price = product.price + color_price
            product_price = product.price
            context['selected_color'] = color
            context['total_price'] = product_price
            context['updated_price'] = total_price

        else:
            pass
        cart = Cart.objects.filter(is_paid=False).first()
        cart_items_count = CartItems.objects.filter(cart=cart).count()
        context['cart_items_count'] = cart_items_count
        return render(request, 'product_details.html', context)
    except Product.DoesNotExist:
        return HttpResponseNotFound("Product not found")
    except Exception as e:
        return HttpResponse("An error occurred: " + str(e), status=500)



@login_required(login_url='/auth/login/')
def add_to_cart(request, uid):
    try:
        product = get_object_or_404(Product, uid=uid)
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)

        size_name = request.GET.get('size')
        color_name = request.GET.get('color')

        # Check if color and size names are provided
        if size_name and color_name:
            # Get the ColorVariant instance for the selected color
            color_variant = get_object_or_404(ColorVariant, product=product, color_name=color_name)
            # Get the SizeVariant instance for the selected size
            size_variants = SizeVariant.objects.filter(product=product, size_name=size_name)
            if size_variants.exists():
                # If multiple variants found, choose the first one
                size_variant = size_variants.first()
            else:
                # No matching size variant found
                size_variant = None
        elif size_name:
            # Get the SizeVariant instance for the selected size
            size_variants = SizeVariant.objects.filter(product=product, size_name=size_name)
            if size_variants.exists():
                # If multiple variants found, choose the first one
                size_variant = size_variants.first()
            else:
                # No matching size variant found
                size_variant = None
            color_variant = None
        elif color_name:
            # Get the ColorVariant instance for the selected color
            color_variant = get_object_or_404(ColorVariant, product=product, color_name=color_name)
            size_variant = None
        else:
            # No color or size specified
            color_variant = None
            size_variant = None

        # Create cart item with selected size and color variants
        cart_item = CartItems.objects.create(
            user=user,
            cart=cart,
            product=product,
            size_variant=size_variant,
            color_variant=color_variant
        )

        # Save the cart item
        cart_item.save()
        
        # Redirect back to the product details page
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except Exception as e:
        return HttpResponse("An error occurred: " + str(e), status=500)


@login_required(login_url='/auth/login/')
def wishlist(request, uid):
    product = get_object_or_404(Product, uid=uid)
    user = request.user
    if user.is_authenticated:
        wish_list = Wishlist.objects.create(user=user, product=product)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
     
        return HttpResponseRedirect('/auth/login/') 
    

@login_required(login_url='/auth/login/')
def wishlist_view(request):
    wish = Wishlist.objects.filter(user=request.user)

    context = {
            'wish_lists':wish,
        }
    return render(request, 'wishlist.html',context)


@login_required(login_url='/auth/login/')
def remove_wishlist(request, wishlist_uid):
    try:
        wish_item = get_object_or_404(Wishlist, uid=wishlist_uid)
        wish_item.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




@login_required(login_url='/auth/login/')
def buy_now(request, uid):
    try:
        product = get_object_or_404(Product, uid=uid)
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)

        size_name = request.GET.get('size')
        color_name = request.GET.get('color')

        # Check if color and size names are provided
        if size_name and color_name:
            # Get the ColorVariant instance for the selected color
            color_variant = get_object_or_404(ColorVariant, product=product, color_name=color_name)
            # Get the SizeVariant instance for the selected size
            size_variants = SizeVariant.objects.filter(product=product, size_name=size_name)
            if size_variants.exists():
                # If multiple variants found, choose the first one
                size_variant = size_variants.first()
            else:
                # No matching size variant found
                size_variant = None
        elif size_name:
            # Get the SizeVariant instance for the selected size
            size_variants = SizeVariant.objects.filter(product=product, size_name=size_name)
            if size_variants.exists():
                # If multiple variants found, choose the first one
                size_variant = size_variants.first()
            else:
                # No matching size variant found
                size_variant = None
            color_variant = None
        elif color_name:
            # Get the ColorVariant instance for the selected color
            color_variant = get_object_or_404(ColorVariant, product=product, color_name=color_name)
            size_variant = None
        else:
            # No color or size specified
            color_variant = None
            size_variant = None

        # Create cart item with selected size and color variants
        cart_item = CartItems.objects.create(
            user=user,
            cart=cart,
            product=product,
            size_variant=size_variant,
            color_variant=color_variant
        )

        # Save the cart item
        cart_item.save()
        return redirect('/cart/')


        # Redirect back to the product details page
        

    except Exception as e:
        return HttpResponse("An error occurred: " + str(e), status=500)
    
@login_required(login_url='/auth/login/')
def cart(request):
    if not request.user.is_authenticated:
        return redirect('/auth/login/')

    context = {}

    try:
        user_cart = Cart.objects.filter(user=request.user, is_paid=False).first()

        if not user_cart:
            cart_items = []
            subtotal = 0
        else:
            cart_items = user_cart.cart_items.all()
            subtotal = sum(cart_item.get_total_price() for cart_item in cart_items)

        context = {
            'cart': user_cart,
            'cart_items': cart_items,
            'total_items': len(cart_items),
            'total_price': user_cart.get_cart_total() if user_cart else 0,
            'subtotal': subtotal,
        }

        if request.method == 'POST':
            coupon_code = request.POST.get('coupon')
            coupon_obj = Coupon.objects.filter(coupon_code__iexact=coupon_code).first()
            context['coupon_obj']=coupon_obj

            if not coupon_obj:
                messages.warning(request, 'Invalid Coupon.')
            elif user_cart.coupon:
                messages.warning(request, 'Coupon already applied.')
            elif user_cart.get_cart_total() < coupon_obj.minimum_amount:
                messages.warning(request, f'Amount should be greater than {coupon_obj.minimum_amount}')
            elif coupon_obj.is_expired:
                messages.warning(request, 'Coupon is expired.')
            else:
                user_cart.coupon = coupon_obj
                user_cart.save()
                messages.success(request, 'Coupon applied.')

            return HttpResponseRedirect(request.path)
        
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        
    return render(request, 'cart.html', context)


@login_required(login_url='/auth/login/')
def remove_coupon(request, cart_uid):
    cart = Cart.objects.get(uid=cart_uid)
    cart.coupon = None
    cart.save()

    messages.success(request, 'Coupon Removed..')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



@login_required(login_url='/auth/login/')
def remove_cart(request, cart_item_uid):
    try:
        cart_item = get_object_or_404(CartItems, uid=cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/auth/login/')
def increase_quantity(request, cart_item_uid):
    cart_item = get_object_or_404(CartItems, uid=cart_item_uid)
    cart_item.increase_quantity()
    total_price = cart_item.get_product_price_with_quantity()
    return JsonResponse({'message': 'Quantity increased successfully', 'total_price': total_price})


@login_required(login_url='/auth/login/')
def decrease_quantity(request, cart_item_uid):
    cart_item = get_object_or_404(CartItems, uid=cart_item_uid)
    cart_item.decrease_quantity()
    total_price = cart_item.get_product_price_with_quantity()
    return JsonResponse({'message': 'Quantity decreased successfully', 'total_price': total_price})



@login_required(login_url='/auth/login/')
def checkout_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')

        try:
            user_cart = Cart.objects.filter(user=request.user, is_paid=False).first()
            if user_cart:
                checkout = Checkout.objects.create(
                    checkout=user_cart,
                    user=request.user,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    mobile=mobile,
                    address1=address1,
                    address2=address2,
                    city=city,
                    state=state,
                    country=country,
                    postal_code=postal_code
                )
                quary = CustomUser.objects.get(id=request.user.id)
                quary.address = address1
                quary.mobile= mobile
                quary.save()
                

                messages.success(request, 'Your checkout information has been successfully saved.')             
                return redirect('/payment_option/')
            else:
                messages.error(request, 'Your cart is empty or not found.')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
    try:
        user_cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        


        if user_cart:
            # If the cart exists, retrieve cart items and calculate subtotal
            cart_items = user_cart.cart_items.all()
            subtotal = sum(cart_item.get_total_price() for cart_item in cart_items)
        else:
            # If the cart doesn't exist, set cart items and subtotal to default values
            cart_items = []
            subtotal = 0
        
        # Prepare context data to be passed to the template
        context = {
            'cart': user_cart,
            'total_price': user_cart.get_cart_total() if user_cart else 0,
            'subtotal': subtotal,
        }

    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        context = {}

    # Render the checkout page with the context data
    return render(request, 'checkout.html', context)



@login_required(login_url='/auth/login/')
def send_order_confirmation_email(request,cart):
    cart_coupon = get_object_or_404(Cart, uid=cart.uid)
    try:
        subject = 'Order Confirmation'
        context = {
            'order_id': cart.order_id,
            'cart': cart.uid,
            'cart_items': cart.cart_items.all(),
            'payment_method': cart.payment_methods,
            'total_amount': cart.total_price,
            'transaction_date': cart.transaction_date,
            'checkout_info': Checkout.objects.all(),
            'coupon': cart_coupon,
        }
        html_message = render_to_string('auth/email.html', context)
        plain_message = strip_tags(html_message)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.user]  # Assuming request.user.email contains the user's email
        message = EmailMultiAlternatives(subject, plain_message, email_from, recipient_list)
        message.attach_alternative(html_message, 'text/html')
        message.send()
    except Exception as e:
        print(f"An error occurred while sending order confirmation email: {str(e)}")


@login_required(login_url='/auth/login/')
def payment_option(request):
    context = {}
    
    try:
        user_cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        
        
        if not user_cart:
            cart_items = []
            subtotal = 0
        else:
            cart_items = user_cart.cart_items.all()
            subtotal = sum(cart_item.get_total_price() for cart_item in cart_items)

        context = {
            'cart': user_cart,  
            'total_price': user_cart.get_cart_total() if user_cart else 0,
            'subtotal': subtotal,
        }

        if request.method == 'POST':
            if 'razorpay' in request.POST:
                if user_cart:
                    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
                    amount_in_paise = int(user_cart.get_cart_total() * 100)  # Convert amount to paise
                    
                    with transaction.atomic():
                        # Creating payment order
                        payment = client.order.create({'amount': amount_in_paise, 'currency': 'INR', 'payment_capture': 1})

                        # Saving Razorpay transaction details
                        razor_transaction = RazorpayTransaction.objects.create(
                            cart=user_cart,
                            amount=user_cart.get_cart_total(),
                            razor_pay_order_id=payment['id'],
                        )

                        user_cart.total_price = user_cart.get_cart_total()
                        user_cart.is_paid = True
                        user_cart.order_id=payment['id']
                        user_cart.payment_methods='Razorpay'
                        user_cart.status = 'Ordered'
                        user_cart.delivery_date = timezone.now() + timedelta(days=4)
                        user_cart.save()
                        
                       
                    context['payment'] = {
                        'id': payment['id'],
                        'amount': user_cart.get_cart_total() * 100  # Pass the amount in paise directly to the template
                    }
                    
            elif 'cod' in request.POST:
                if user_cart:
                    # Saving COD transaction details
                    cod = CODTransaction.objects.create(
                        cart=user_cart,
                        amount=user_cart.get_cart_total(),
                    )
                    
                    user_cart.total_price = user_cart.get_cart_total()
                    user_cart.is_paid = True
                    user_cart.payment_methods = 'COD'
                    user_cart.order_id=cod.order_id                   
                    user_cart.status = 'Ordered'
                    user_cart.delivery_date = timezone.now() + timedelta(days=4)
                    user_cart.save()      
                    send_order_confirmation_email(request,
                        user_cart
                    )         

                    return redirect('/success_cod/')  # Redirect to the homepage after successful COD payment

    except BadRequestError as e:
        messages.error(request, f'Razorpay bad request error: {e}')
    except ServerError as e:
        messages.error(request, f'Razorpay server error: {e}')
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')

    return render(request, 'payment_page.html', context)


@login_required(login_url='/auth/login/')
def success_razorpay(request):
    try:
        order_id = request.GET.get('razorpay_order_id')
        razor_transaction = RazorpayTransaction.objects.get(razor_pay_order_id=order_id)

        razor_transaction.is_paid = True
        razor_transaction.save()
        send_order_confirmation_email(request,razor_transaction.cart)
        
        amount = razor_transaction.amount
        date = razor_transaction.transaction_date
        cart_uid = razor_transaction.cart.uid
        file_name, pdf_generated = generate_invoice_pdf(cart_uid)
        if pdf_generated:
            context={
                'cart_uid': cart_uid,
                'amount':amount,
                'date':date,
                'file_name': file_name,
            }
        # Assuming you want to mark the corresponding cart as paid as well
        if razor_transaction.cart:
            razor_transaction.cart.is_paid = True
            razor_transaction.cart.save()
            


        return render(request,'success.html',context)
    except ObjectDoesNotExist:
        return HttpResponse('Transaction does not exist for the provided order ID.')


@login_required(login_url='/auth/login/')
def success_cod(request):
    try:
        cod_transaction = CODTransaction.objects.latest('transaction_date')
        cart_uid = cod_transaction.cart.uid

        file_name, pdf_generated = generate_invoice_pdf(cart_uid)

        if pdf_generated:
            context = {
                'cart_uid': cart_uid,
                'date': cod_transaction.transaction_date,
                'file_name': file_name,
            }

            return render(request, 'order_success.html', context)
        else:
            return HttpResponse('PDF generation failed. Please try again later.')

    except CODTransaction.DoesNotExist:
        return HttpResponse('No cash on delivery transactions found.')


@login_required(login_url='/auth/login/')
def profile(request):
    return render(request, 'auth/profile.html')

@login_required(login_url='/auth/login/')
def profile_edit(request,user_id):
    try:
        quary = CustomUser.objects.get(id = user_id)

        if request.method == 'POST':
            email = request.POST.get('email')
            name = request.POST.get('name')
            address = request.POST.get('address')
            mobile = request.POST.get('mobile')

            quary.email =email
            quary.name = name
            quary.address = address
            quary.mobile = mobile
            quary.save()
            messages.success(request, 'Account information change successfully.')
            return redirect('/profile/')
    except Exception as e:
        messages.error(request, e)
    return render(request, 'auth/profile_edit.html')


@login_required(login_url='/auth/login/')
def order_list(request):
    orders = Cart.objects.filter(user=request.user, is_paid=True).prefetch_related('cart_items').all()

    context = {
        'orderlists': orders
    }
    return render(request, 'orderlist.html', context)



@login_required(login_url='/auth/login/')
def order_details(request, order_id):
    try:
        cod_transaction = CODTransaction.objects.latest('transaction_date')
        cart_uid = cod_transaction.cart.uid

        file_name, pdf_generated = generate_invoice_pdf(cart_uid)

        context = {}

        if pdf_generated:
            context.update({
                'cart_uid': cart_uid,
                'date': cod_transaction.transaction_date,
                'file_name': file_name,
            })

        order = get_object_or_404(Cart, uid=order_id, user=request.user)
        cart_items = order.cart_items.all()

        context.update({'order': order, 'cart_items': cart_items})

    except Exception as e:
        messages.error(request, str(e))
        context = {}  # Clear context in case of an error

    return render(request, 'order_details.html', context)


@login_required(login_url='/auth/login/')
def order_cancel(request, cart_uid):
    try:
        order = get_object_or_404(Cart, uid=cart_uid, user=request.user)
        cart_items = order.cart_items.all()
        context = {'order': order, 'cart_items': cart_items}
        cart = get_object_or_404(Cart, uid=cart_uid)
        user = request.user
        if request.method == 'POST':
            cancellation_reason = request.POST.get('cancellation_reason')
            cancel_order = OrderCancel.objects.create(cart=cart, user=user, cancellation_reason=cancellation_reason)
            context = {'cancel_order': cancel_order}
            cart.status = 'Cancelled'
            cart.save()
            messages.success(request, 'Order cancelled successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        return render(request, 'order_cancel.html',context) 
    except Exception as e:
        messages.error(request, str(e))
         
         
@login_required(login_url='/auth/login/')
def order_return(request, cart_uid):
    try:
        order = get_object_or_404(Cart, uid=cart_uid, user=request.user)
        cart_items = order.cart_items.all()
        context = {'order': order, 'cart_items': cart_items}
        
        if request.method == 'POST':
            return_reason = request.POST.get('return_reason')
            return_date = timezone.now() + timedelta(days=10)  
            status = 'Requested'
            return_order = ReturnStatus.objects.create(cart=order, user=request.user, return_reason=return_reason, status=status, return_date=return_date)
            context = {'return_order':return_order}
            order.status = 'Return'  
            order.save()
            messages.success(request, 'Order return request applied successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return render(request, 'order_return.html', context) 
    except Exception as e:
        messages.error(request, str(e))
    
    return render(request, 'order_return.html', context)


@login_required(login_url='/auth/login/')
def order_return_tracker(request, order_id):
    order = get_object_or_404(ReturnStatus, cart__uid=order_id, user=request.user)
    cart_items = order.cart.cart_items.all() 
    context = {'order': order, 'cart_items': cart_items}
    return render(request, 'order_return_tracker.html', context)



@login_required(login_url='/auth/login/')
def contactus(request):
    try:
        if request.method == 'POST':
            name = request.POST['name']
            email = request.POST['email']
            message = request.POST['message']
            ContactUs.objects.create(
                name= name,
                email = email, 
                message = message
            )
            messages.success(request, 'We will get back soon....')
    except Exception as e:
        messages.error(request, str(e))
    finally:
        return render(request,'auth/contactus.html' )