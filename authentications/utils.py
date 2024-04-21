from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
import uuid
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail , EmailMultiAlternatives
from django.utils.html import strip_tags


from django.core.mail import send_mail
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user,timestamp):
        return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_active))
    
generate_token=TokenGenerator()


'''def send_forget_password_mail(email,token):
    subject = 'Your forget password link'
    message = f'Hi , click on the link to reset your password http://127.0.0.1:8000/auth/change_password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject,message,email_from,recipient_list)
    return True
'''

def send_forget_password_mail(email , token):
    subject = 'Your forget password link'
    html_message = render_to_string('auth/email_forget_password.html',{ "token" : token,})
    plain_message = strip_tags(html_message)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    message = EmailMultiAlternatives(subject, plain_message, email_from, recipient_list)
    message.attach_alternative(html_message, 'text/html')
    message.send()
    return True



