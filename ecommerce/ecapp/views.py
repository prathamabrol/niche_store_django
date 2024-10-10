from django.shortcuts import render,redirect,HttpResponse
from ecapp.models import Contact,Product,Orders,OrderUpdate
from django.contrib import messages
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# FOLLOWING IMPORTS ARE FOR SENDING EMAILS.
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.core import mail
from django.conf import settings
from math import ceil

# FOR PAYMENT INTEGRATION.
import razorpay

# Create your views here.

def index(request):

    allProds = []
    catprods = Product.objects.values('category','id')
    # print(catprods)
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}

    return render(request,"index.html",params)


def contact(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')
    
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        desc = request.POST.get("desc")
        pnumber = request.POST.get("pnumber")
        
        # Save the contact form data to the database
        myquery = Contact(name=name, email=email, desc=desc, phonenumber=pnumber)
        myquery.save()
        
        # Email sending
        from_email = settings.EMAIL_HOST_USER
        connection = mail.get_connection()
        connection.open()
        
        # Email to site owner
        email_message = mail.EmailMessage(
            subject=f'Email from {name}',
            body=f'UserEmail: {email}\nUserPhoneNumber: {pnumber}\n\nQuery: {desc}',
            from_email=from_email,
            to=['prathamabrol.sknsits.it@gmail.com'],
            connection=connection
        )
        
        # Prepare the response email to the user
        email_subject_client = "Swift Cart - We Received Your Query"
        html_content_client = render_to_string('contact_response.html', {
            'name': name,
            'query': desc,
        })
        text_content_client = strip_tags(html_content_client)  # Create plain text version
        
        # Email response to the user
        email_client = EmailMultiAlternatives(
            subject=email_subject_client,
            body=text_content_client,
            from_email=from_email,
            to=[email],
            connection=connection
        )
        email_client.attach_alternative(html_content_client, "text/html")
        
        # Send both emails
        connection.send_messages([email_message, email_client])
        connection.close()
        
        messages.info(request, "Thank you for reaching us. We will get back to you soon...")
        
    return render(request, "contact.html")

def about(request):
    return render(request,"about.html")








def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')


    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '') 
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        Order = Orders(
            items_json=items_json,
            amount=amount,
            name=name,
            email=email,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone
        )
        
        
        
        Order.save()
        
        is_thank = True
        
    #  unique OID for the order

        id = Order.order_id
        oid=str(id)+"SwiftCart"
        
        Order.oid = oid
        Order.save()
        
        # Razorpay Payment Integration
        
        client = razorpay.Client(auth=('rzp_test_R7kWkFU6ZllnWF', 'W0gE85soRmV6WanAQr1nW69n'))
        payment_data = {
            'amount': int(Order.amount) * 100,  # Amount in paise
            'currency': 'INR',  # Currency code (INR for Indian Rupee)
            'receipt': f'order_{Order.oid}',
            'payment_capture': 1,  # Auto-capture payment
            
        }

        payment = client.order.create(data=payment_data)
        
        if payment:
            Order.paymentstatus = "Success"
            Order.amountpaid = amount  # Set the amount paid
            Order.save()

        return render(request, 'razorpay_checkout.html', {'order': Order, 'payment': payment})

    return render(request, 'checkout.html')





def payment_status(request):
    payment_id = request.GET.get('payment_id')
    
    # Retrieve the order based on the order id (assuming you have oid)
    oid = request.GET.get('oid')
    order = Orders.objects.filter(oid=oid).first()
    
    is_success = order is not None and order.paymentstatus == "Success"
    
    context = {
        'payment_id': payment_id,
        'is_success': is_success,
        'oid': order.oid if order else None,
        'amount_paid': order.amountpaid if order else None,
    }
    return render(request, 'payment_status.html', context)




def generate_invoice(request, order_id):
    try:
        order = Orders.objects.get(oid=order_id)  # Get the order details
    except Orders.DoesNotExist:
        return HttpResponse("Order not found.", status=404)

    # Create a HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.oid}.pdf"'

    # Create a PDF canvas
    pdf_file = SimpleDocTemplate(response, pagesize=letter)

    # Elements to add to the PDF
    elements = []

    # Add logo
    
    logo = Image("C:\DJANGO-MAIN\ecommerce\static\images\LOGOO.png", 2 * inch, 2 * inch)  # Adjust the size as needed
    elements.append(logo)
    elements.append(Spacer(1, 0.5 * inch))
    
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("<strong>SwiftCart Invoice</strong>", getSampleStyleSheet()['Title']))
    elements.append(Spacer(1, 0.25 * inch))

    # Create a table for order details
    data = [
        ['Order ID', order.oid],
        ['Customer Name', order.name],
        ['Email', order.email],
        ['Amount', f'Rs.{order.amount} /-'],
        ['Address', f"{order.address1}, {order.city}, {order.state}, {order.zip_code}"],
    ]

    # Create the table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Add table to elements
    elements.append(table)

    # Add a footer
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Thank you for your business!", getSampleStyleSheet()['Normal']))
    elements.append(Spacer(1, 0.5 * inch))

    # Build the PDF
    pdf_file.build(elements)

    return response