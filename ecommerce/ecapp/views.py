from django.shortcuts import render,redirect,HttpResponse
from ecapp.models import Contact,Product,Orders,OrderUpdate
from django.contrib import messages
from datetime import datetime

# FOLLOWING IMPORTS ARE FOR SENDING EMAILS.
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.core import mail
from django.conf import settings
from math import ceil
# FOR PAYMENT INTEGRATION.
import razorpay
from django.http import JsonResponse

# FOR PAYMENT INTEGRATION.
from django.views.decorators.csrf import csrf_exempt

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
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')
    
    if request.method == "POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        
        # Email sending.
        from_email=settings.EMAIL_HOST_USER
        connection=mail.get_connection()
        connection.open()
        email_message = mail.EmailMessage(
        f'Email from {name}',
        f'UserEmail: {email}\nUserPhoneNumber: {pnumber}\n\nQuery: {desc}',
        from_email,
        ['prathamabrol.sknsits.it@gmail.com'],
        connection=connection)
        
        email_client = mail.EmailMessage(
        f'Swift Cart Response',
        f'Thanks for reaching us. We will get back to you soon...\n\nSwift Cart\n9906281719\nprathamabrol0@gmail.com',
        from_email,
        [email],
        connection=connection)

        connection.send_messages([email_message,email_client])
        connection.close()
        
        messages.info(request,"Thank You for reaching us.We will get back to you soon...")
        
        
        
    return render(request,"contact.html",)


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
        
        id = Order.order_id
        oid=str(id)+"SwiftCart"
        
        Order.oid = oid
        Order.save()
        
        
        client = razorpay.Client(auth=('rzp_test_R7kWkFU6ZllnWF', 'W0gE85soRmV6WanAQr1nW69n'))
        payment_data = {
            'amount': int(Order.amount) * 100,  # Amount in paise
            'currency': 'INR',  # Currency code (INR for Indian Rupee)
            'receipt': f'order_{Order.oid}',
            'payment_capture': 1,  # Auto-capture payment
            # Add additional parameters as needed
        }

        payment = client.order.create(data=payment_data)

        return render(request, 'razorpay_checkout.html', {'order': Order, 'payment': payment})

    return render(request, 'checkout.html')






def payment_status(request):
    print(request.GET)

    payment_id = request.GET.get('payment_id')
    
    is_success = True
    context = {
        'payment_id': payment_id,
        'is_success': is_success,
    }
    return render(request, 'payment_status.html', context)








