from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from .models import*
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.conf import settings
#from django.utils.encoding import force_text
from django.views.generic import View
from django.utils.encoding import DjangoUnicodeDecodeError
from django.core.mail import send_mail
from .utils import *
from django.template.loader import render_to_string
from django.core.mail import send_mail , EmailMultiAlternatives
from django.utils.html import strip_tags
from ecommerceApp.models import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings



def register(request): 
    if request.method == "POST":
        email = request.POST.get('email')
        name = request.POST.get('name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        try:
            validate_password(password1)
        except ValidationError as e:
            messages.error(request, '\n'.join(e))
            return redirect('/auth/signup/')
        
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('/auth/signup/')
           
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already taken!")
            return redirect('/auth/signup/')

        user = CustomUser(email=email, name=name)
        user.set_password(password1)
        user.is_active = False
        user.save()

        subject = 'Activate Your Account'
        html_message = render_to_string('auth/activate.html', {
            'user': user,
            'domain': request.get_host(),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })
        plain_message = strip_tags(html_message)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email, ]
        message = EmailMultiAlternatives(subject, plain_message, email_from, recipient_list)
        message.attach_alternative(html_message, 'text/html')
        
        try:
            message.send()
            messages.success(request, 'An activation email has been sent to your email address.')
        except Exception as e:
            messages.error(request, f"An error occurred while sending the activation email: {e}")
        
        return redirect('/auth/login/')

    return render(request, 'auth/signup.html')





def send_order_confirmation_email(cart):
    user_email = cart.user.email  # Assuming cart has a user field referencing the CustomUser model
    
    try:
        subject = 'Order Confirmation'
        context = {
            'order_id': cart.order_id,
            'cart_items': cart.cart_items.all(),
            'payment_method': cart.payment_methods,
            'total_amount': cart.total_price,
            'transaction_date': cart.transaction_date,
            'checkout_info': Checkout.objects.all(),
        }
        html_message = render_to_string('auth/email.html', context)
        plain_message = strip_tags(html_message)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user_email, ]
        message = EmailMultiAlternatives(subject, plain_message, email_from, recipient_list)
        message.attach_alternative(html_message, 'text/html')
        message.send()
    except Exception as e:
        print(f"An error occurred while sending order confirmation email: {str(e)}")


def login_form(request): 
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password1')
        
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Invalid email address! ')
            return redirect('/auth/login/')
        
        user = authenticate(email=email, password=password)
        
        if user is None:
            messages.error(request, 'Invalid email or password! or check email Activate Your Account ')
            return redirect('/auth/login/')
    
        else:
            login(request, user)
            return redirect('/') 

    return render(request, 'auth/login.html')

def logout_page(request):
    logout(request)
    messages.info(request,'Logout Successfully ')
    return redirect('/')


    
class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except Exception as e:
            user = None
        
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.info(request, 'Account Activated Successfully')
            return redirect('/auth/login')
        return render(request, 'auth/activatefail.html')
    


def change_password(request, token):
    context ={}
    try:
        profile_obj = Profile.objects.filter(forget_password_token = token).first()
        
        if request.method == 'POST':
            newpassword = request.POST.get('newpassword')
            confirm_password = request.POST.get('confirm_password')
            user_id = request.POST.get('user_id')

            if user_id is None:
                messages.error(request, 'No User id found.')
                return redirect(f'/change_password/{token}/')
            
            if newpassword != confirm_password:
                messages.error(request, 'Both password are equal.')
                return redirect(f'/change_password/{token}/')

            user_obj = CustomUser.objects.get(id = user_id)
            user_obj.set_password(newpassword)
            user_obj.save()
            return redirect('/auth/login/')
        
        context ={'user_id': profile_obj.user.id}
    except Exception as e:
        messages.info(request, e)
    return render(request, 'auth/change_password.html',context)


'''
def forgetPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()
        
        if user:
            try:
                profile = Profile.objects.create(user=user)
                token = str(uuid.uuid4())
                profile.forget_password_token = token
                profile.save()
                send_forget_password_mail(user.email, token)
                messages.success(request, 'An email has been sent.')
            except Profile.DoesNotExist:
                messages.error(request, 'No user found with this email.')
        else:
            messages.error(request, 'No user found with this email.')

        return redirect('/auth/forget_password/')  
    return render(request, 'auth/forget_password.html')
'''
def forgetPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if user:
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user)
            token = str(uuid.uuid4())
            profile.forget_password_token = token
            profile.save()
            send_forget_password_mail(user.email, token)
            messages.success(request, 'An email has been sent.')
        else:
            messages.error(request, 'No user found with this email.')
        return redirect('/auth/forget_password/')  
    return render(request, 'auth/forget_password.html')