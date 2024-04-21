from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from ecommerceApp.models import *

'''def invioce_pdf(request,cart_uid):


    return render(request, 'pdfs/invoice.html')

def save_pdf(params: dict):
    # Load the HTML template

    template = get_template("pdfs/invoice.html")
    html = template.render(params)

    # Create BytesIO buffer to store the PDF
    response = BytesIO()

    # Generate PDF and write to BytesIO buffer
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response)

    # Check if PDF generation was successful
    if pdf.err:
        print("PDF generation failed:", pdf.err)
        return None, False

    # Generate a unique filename
    file_name = str(uuid.uuid4())

    # Write PDF content to a file in the static directory
    try:
        file_path = os.path.join(settings.BASE_DIR, "static", f"{file_name}.pdf")
        with open(file_path, 'wb+') as output:
            output.write(response.getvalue())

    except Exception as e:
        print("Error saving PDF:", e)
        return None, False

    # Return the generated filename
    return file_name, True
'''

'''def save_pdf(params:dict):
    template = get_template("pdfs/invoice.html")
    html = template.render(params)
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response)
    file_name = uuid.uuid4()

    try:
        with open(str(settings.BASE_DIR)+ f'/public/static/{file_name}.pdf', 'wb+') as output:
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), output)

    except Exception as e:
        print("Error saving PDF:", e)
    
    if pdf.err:    
        return None, False

    # Return the generated filename
    return file_name, True'''

from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
from io import BytesIO
from xhtml2pdf import pisa
# Import your Cart and Checkout models


    
'''def save_pdf(params:dict):
    template = get_template("pdfs/invoice.html")
    html = template.render(params)
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response)
    file_name = uuid.uuid4()

    try:
        with open(str(settings.BASE_DIR)+ f'/public/static/{file_name}.pdf', 'wb+') as output:
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), output)

    except Exception as e:
        print("Error saving PDF:", e)
    
    if pdf.err:    
        return None, False

    # Return the generated filename
    return file_name, True'''
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from xhtml2pdf import pisa
import os
from io import BytesIO

'''def invoice_pdf(request, cart_uid):
    try:
        # Retrieve cart details based on the cart UID
        cart = get_object_or_404(Cart, uid=cart_uid)
        
        # Retrieve cart items
        cart_items = cart.cart_items.all()
        
        # Retrieve checkout details based on the cart UID
        checkout = get_object_or_404(Checkout, uid=cart_uid)
        
        # Extract relevant data
        payment_method = cart.payment_methods
        total_amount = cart.total_price
        name = checkout.first_name
        shipping_address = checkout.address1
        mobile_number = checkout.mobile
        transaction_date = cart.transaction_date
        order_id = cart.order_id

        # Prepare data to pass to the template
        context = {
            'order_id': order_id,
            'cart_items': cart_items,
            'payment_method': payment_method,
            'name': name,
            'shipping_address': shipping_address,
            'mobile_number': mobile_number,
            'transaction_date': transaction_date,
            'total_amount': total_amount,
            'request': request  # Pass request object to access request.user
        }

        # Render the Invoice.html template
        template = get_template('pdfs/invoice.html')
        html_content = template.render(context)
        
        # Generate PDF
        pdf_data = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_content.encode('UTF-8')), pdf_data)
        
        if pdf.err:
            return HttpResponse('Failed to generate PDF.')

        # Set the file name
        file_name = f'{uuid.uuid4()}.pdf'
        file_path = os.path.join(settings.BASE_DIR, 'public', 'static', file_name)
        
        # Save PDF to file
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(pdf_data.getvalue())

        # Return the generated file name and response with PDF attachment
        response = HttpResponse(pdf_data.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

    except Cart.DoesNotExist:
        return HttpResponse('Cart does not exist.')
    except Checkout.DoesNotExist:
        return HttpResponse('Checkout does not exist for the provided cart.')'''

from django.http import Http404,HttpResponseNotFound

import os
from django.conf import settings
from django.http import FileResponse
from django.conf import settings
import os
from django.http import HttpResponseServerError




def generate_invoice_pdf(cart_uid):
    try:
        cart = get_object_or_404(Cart, uid=cart_uid)
        cart_items = cart.cart_items.all()
        subtotal = sum(cart_item.get_total_price() for cart_item in cart_items)
        
        
        try:
            checkout = Checkout.objects.get(uid=cart_uid)
            
        except Checkout.DoesNotExist:
            checkout = None
        
        payment_method = cart.payment_methods
        total_amount = cart.total_price
        order_id = cart.order_id
        transcation_date=cart.transaction_date
        checkout_info = Checkout.objects.all()



        # Prepare data to pass to the template
        context = {
            'order_id': order_id,
            'cart_items': cart_items,
            'payment_method': payment_method,
            'checkout': checkout,
            'total_amount': total_amount,
            'transcation_date':transcation_date,
            'checkout_info':checkout_info,
            'cart': cart,
            'subtotal': subtotal
        }

        template = get_template('pdfs/invoice.html')
        html_content = template.render(context)
        
        pdf_bytes = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_content.encode('UTF-8')), pdf_bytes)
        
        if not pdf.err:
            file_name = f"{uuid.uuid4()}.pdf"
            file_path = os.path.join(settings.BASE_DIR, 'static', file_name)
            with open(file_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes.getvalue())
            
            return file_name, True
        else:
            print("Error generating PDF:", pdf.err)
            return None, False

    except Cart.DoesNotExist:
        print("Cart does not exist.")
        return None, False

from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings
import os

def download_pdf(request, file_name):
    try:
        file_path = os.path.join(settings.BASE_DIR, 'static', file_name)
        with open(file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            new_file_name = "invoice.pdf"  # Change this to the desired new file name
            response['Content-Disposition'] = f'attachment; filename="{new_file_name}"'
            return response
    except FileNotFoundError:
        return HttpResponseNotFound("PDF file not found.")
    except Exception as e:
        # Log the error for debugging purposes
        print("Error downloading PDF:", e)
        # Return a 500 Internal Server Error response
        return HttpResponseServerError("An error occurred while downloading the PDF file.")
