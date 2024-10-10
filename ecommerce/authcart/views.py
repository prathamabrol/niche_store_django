from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages 
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.hashers import check_password
# FOLLOWING IMPORTS ARE FOR SENDING EMAILS.
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from .utils import TokenGenerator,generate_token
from django.core.mail.message import EmailMessage
from django.conf import settings
from django.utils.html import strip_tags


from django.core.mail import send_mail
from django.core import mail


# Create your views here.

def signup(request):
    if request.method == "POST":
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        confirm_password = request.POST.get('pass2')

        if pass1 != confirm_password:
            messages.warning(request, "Password is not Matching")
            return render(request, "signup.html")
        
        elif email == '' or pass1 == '' or confirm_password == '': 
            messages.warning(request, "Fields cannot be Empty")
            return render(request, "signup.html")

        try:
            if User.objects.get(username=email):
                messages.info(request, "Email is already Taken.")
                return render(request, "signup.html")
        except User.DoesNotExist:
            pass

        user = User.objects.create(username=email, email=email)
        user.set_password(pass1)
        user.is_active = False
        user.save()
        
        # Prepare email details
        email_subject = "Activate Your Account"
        html_content = render_to_string('activate.html', {
            'user': user,
            'domain': '127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })
        text_content = strip_tags(html_content)  # Create a plain text version of the email

        # Create email
        email_message = EmailMultiAlternatives(email_subject, text_content, settings.EMAIL_HOST_USER, [email])
        email_message.attach_alternative(html_content, 'text/html')  # Attach HTML content
        email_message.send()

        messages.success(request, "Activate your account by clicking the link in your mail.")
        return render(request, "login.html")
    else:
        return render(request, "signup.html")

class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated Successfully")
            return redirect('/auth/login')
        return render(request,'activatefail.html')



     


def handlelogin(request):
    if request.method == "POST":
        username = request.POST.get('email')
        u_pass = request.POST.get('pass1') 
        

        myuser=authenticate(username=username,password=u_pass)
        print(myuser)
        if myuser is not None:
            login(request,myuser)
            
            return redirect('/')
        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/auth/login')   
    
    return render(request,"login.html")


    #     try:
    #         user = User.objects.get(email=username)
    #         print(user)
    #     except User.DoesNotExist:
    #         user = None
            
            
    #     if user is not None:

    #         if check_password(u_pass,user.password):

    #             login(request, user)
    #             messages.success(request, "Login Successfully")
    #             # return redirect('/')
    #             return HttpResponse('LOGIN DONE')
        
    #         else:
    #             # messages.error(request,"Invalid email or password.")
    #             return HttpResponse('INVALID P AND U')

                
    #     else:
    #             # messages.error(request,"User does not exist.")
    #             return HttpResponse('DOESNOT EXIXT')

                
    # return render(request, "authentication/login.html")
    
    
    
def handlelogout(request):
    logout(request)
    messages.info(request,"Logout Success")
    return redirect('/auth/login')


