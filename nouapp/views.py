from django.shortcuts import render, redirect, reverse
from . models import Enquiry, Student, Login
from datetime import date
from django.contrib import messages
from adminapp.models import Program, Branch, Year
from django.core.mail import send_mail
from django.conf import settings
from . import smssender
from adminapp.models import News


from django.http import JsonResponse
from django.views.decorators.http import require_POST

# Add these imports at the top of nouapp/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .chatbot_logic import chatbot

# Add this view function to nouapp/views.py
@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)
            
        bot_response, tag = chatbot.get_response(user_message)
        return JsonResponse({'response': bot_response, 'tag': tag})
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Server error', 'details': str(e)}, status=500)
    
@require_POST
def set_theme(request):
    theme = request.POST.get('theme', 'light')
    request.session['theme'] = theme
    return JsonResponse({'status': 'ok'})

from rest_framework import generics
from .serializers import StudentSerializer

class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'rollno' # Assuming rollno is the primary key for Student model

# Create your views here.
def index(request):


def aboutus(request):
    ns=News.objects.all()
    return render(request,"aboutus.html",locals())

def registration(request):
    if request.method=="POST":
        rollno=request.POST['rollno']
        name=request.POST['name']
        fname=request.POST['fatherName']
        mname=request.POST['motherName']
        gender=request.POST['gender']
        address=request.POST['address']
        program=request.POST['program']
        branch=request.POST['branch']
        year=request.POST['year']
        contactno=request.POST['contactNo']
        emailaddress=request.POST['emailAddress']
        password=request.POST['password']
        regdate=date.today()
        usertype='student'
        status='false'
        stu=Student(rollno=rollno,name=name,fname=fname,mname=mname,gender=gender,address=address,program=program,branch=branch,year=year,contactno=contactno,emailaddress=emailaddress,regdate=regdate)
        log=Login(userid=rollno,password=password,usertype=usertype,status=status)
        stu.save()
        log.save()
        # subject='Important Email from Nalanda Open University'
        # msg=f'Hello, {name} your registration is successfull. Your password is {password}'
        # email_from=settings.EMAIL_HOST_USER
        # send_mail(subject,msg,email_from,[emailaddress])
        messages.success(request,'Your Registration is submited')
    program=Program.objects.all()
    branch=Branch.objects.all()
    year=Year.objects.all()
    ns=News.objects.all()
    return render(request,"registration.html",locals())

def login(request):
    if request.method=="POST":
        userid=request.POST['userid']
        password=request.POST['password']
        usertype=request.POST['usertype']
        try:
            obj=Login.objects.get(userid=userid,password=password)
            if obj.usertype=="student":
                request.session['rollno']=userid    #create session variable
                return redirect(reverse('studentapp:studenthome'))
            elif obj.usertype=="admin":
                request.session['adminid']=userid
                return redirect(reverse('adminapp:adminhome'))
        except:
            messages.success(request,'Invalid user')
    ns=News.objects.all()
    return render(request,"login.html",locals())

def contactus(request):
    if request.method=="POST":
        name=request.POST['name']
        gender=request.POST['gender']
        address=request.POST['address']
        contactno=request.POST['contactno']
        emailaddress=request.POST['emailaddress']
        enquirytext=request.POST['enquirytext']
        enquirydate=date.today()
        enq=Enquiry(name=name,gender=gender,address=address,contactno=contactno,emailaddress=emailaddress,enquirytext=enquirytext,enquirydate=enquirydate)
        enq.save()
        # smssender.sendsms(contactno)
        messages.success(request,'Your Enquiry is submited')
    ns=News.objects.all()
    return render(request,"contactus.html",locals())

def courses(request):
    return render(request,"courses.html")

def services(request):
    return render(request,"services.html")


#_____________________________this is for forgot password / reset password logic views_______________________________
import uuid
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.urls import reverse

# Store reset tokens temporarily (in production, use database or cache)
reset_tokens = {}

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        try:
            student = Student.objects.get(emailaddress=email)
            
            if Login.objects.filter(userid=student.rollno).exists():
                login_user = Login.objects.get(userid=student.rollno)
                
                # Generate unique reset token
                reset_token = str(uuid.uuid4())
                
                # Store token
                reset_tokens[reset_token] = login_user.userid
                
                # Create reset link
                reset_link = request.build_absolute_uri(
                    reverse('nouapp:reset_password', args=[reset_token])
                )

                # Show link directly instead of sending email
                return render(request, "show_reset_link.html", {"reset_link": reset_link})
            
            else:
                messages.error(request, "No login found for this email")
        except Student.DoesNotExist:
            messages.error(request, "Email not registered")
    
    return render(request, "forgot_password.html")

def reset_password(request, token):
    if token not in reset_tokens:
        messages.error(request, "Invalid or expired link")
        return render(request, "reset_password.html", {"token": token})

    userid = reset_tokens[token]

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if not new_password or not confirm_password:
            messages.error(request, "Please fill in both password fields")
            return render(request, 'reset_password.html', {'token': token})

        if len(new_password) > 30:
            messages.error(request, 'Password cannot be longer than 30 characters')
            return render(request, 'reset_password.html', {'token': token})

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'reset_password.html', {'token': token})

        try:
            login_user = Login.objects.get(userid=userid)
            login_user.password = new_password
            login_user.save()

            # Delete token after use
            del reset_tokens[token]
            
            messages.success(request, "Password reset successfully! You can now login with your new password.")
            return redirect('nouapp:login')
            
        except Login.DoesNotExist:
            messages.error(request, 'User not found')
            return render(request, 'reset_password.html', {'token': token})

    return render(request, "reset_password.html", {"token": token})
