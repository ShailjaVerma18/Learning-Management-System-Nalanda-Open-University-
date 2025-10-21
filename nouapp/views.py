from django.shortcuts import render, redirect, reverse
from . models import Enquiry, Student, Login
from datetime import date
from django.contrib import messages
from adminapp.models import Program, Branch, Year
from django.core.mail import send_mail
from django.conf import settings
from . import smssender
from adminapp.models import News
from django.db.models import Q
from django.core.paginator import Paginator


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

# Create your views here.
def index(request):
    ns=News.objects.all()
    return render(request,"index.html",locals())

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
        program_id=request.POST['program']  # This comes as ID from form
        branch_id=request.POST['branch']    # This comes as ID from form
        year_id=request.POST['year']        # This comes as ID from form
        contactno=request.POST['contactNo']
        emailaddress=request.POST['emailAddress']
        password=request.POST['password']
        regdate=date.today()
        usertype='student'
        status='false'
        
        # FIXED: Get the actual objects, not strings
        try:
            program_obj = Program.objects.get(id=program_id)
            branch_obj = Branch.objects.get(id=branch_id)
            year_obj = Year.objects.get(id=year_id)
            
            stu=Student(rollno=rollno,name=name,fname=fname,mname=mname,gender=gender,
                       address=address,program=program_obj,branch=branch_obj,year=year_obj,
                       contactno=contactno,emailaddress=emailaddress,regdate=regdate)
            log=Login(userid=rollno,password=password,usertype=usertype,status=status)
            stu.save()
            log.save()
            messages.success(request,'Your Registration is submitted')
        except (Program.DoesNotExist, Branch.DoesNotExist, Year.DoesNotExist):
            messages.error(request,'Invalid program, branch, or year selected')
        except Exception as e:
            messages.error(request,f'Registration failed: {str(e)}')
            
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


# _____________________________this is for forgot password / reset password logic views_______________________________
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
# def search_view(request):
#     query = request.GET.get('q', '').strip()
#     results = []
#     message = ''

#     if query:
#         # Check if query is a number for rollno search
#         if query.isdigit():
#             results = Student.objects.filter(
#                 Q(rollno=query) |
#                 Q(name__icontains=query) |
#                 Q(program__icontains=query) |
#                 Q(branch__icontains=query) |
#                 Q(contactno__icontains=query)
#             ).distinct()
#         else:
#             results = Student.objects.filter(
#                 Q(name__icontains=query) |
#                 Q(program__icontains=query) |
#                 Q(branch__icontains=query) |
#                 Q(contactno__icontains=query)
#             ).distinct()

#         if not results.exists():
#             message = f"No results found for '{query}'."
#     else:
#         message = "Please enter a search term."

#     return render(request, 'search_results.html', {
#         'query': query,
#         'results': results,
#         'message': message
#     })

def search_view(request):
    query = request.GET.get('q', '').strip()
    results = []
    message = ''

    if query:
        if query.isdigit():
            results = Student.objects.filter(
                Q(rollno=query) |
                Q(name__icontains=query) |
                Q(program__icontains=query) |
                Q(branch__icontains=query) |
                Q(contactno__icontains=query)
            ).distinct()
        else:
            results = Student.objects.filter(
                Q(name__icontains=query) |
                Q(program__icontains=query) |
                Q(branch__icontains=query) |
                Q(contactno__icontains=query)
            ).distinct()

        if not results.exists():
            message = f"No results found for '{query}'."
    else:
        message = "Please enter a search term."

    # Debug print
    print("Query:", query)
    print("Results:", results)

    # return render(request, 'search_results.html', {
    #     'query': query,
    #     'results': results,
    #     'message': message
    # })
    return render(request, 'search_results.html', {
        'query': query,
        'results': results,
        'message': message
    })


# ---------------------------
# Schema normalization helpers
# ---------------------------

def migrate_existing_students():
    """
    Utility function to migrate any existing students with string values
    to use ForeignKey relationships. Run this once after updating your models.
    """
    from django.db import transaction
    from adminapp.models import Program, Branch, Year
    
    try:
        with transaction.atomic():
            students = Student.objects.all()
            
            for student in students:
                if isinstance(student.program, str):
                    program_obj, created = Program.objects.get_or_create(program=student.program)
                    if created:
                        print(f"Created Program: {student.program}")
                    # Note: You’d normally handle this in a custom migration
                
                # Similar logic can be applied for branch and year...
                
            print("Migration completed successfully")
            
    except Exception as e:
        print(f"Error during migration: {e}")


def ensure_dropdown_data():
    """
    Ensure basic Program, Branch, Year data exists for dropdowns
    """
    from adminapp.models import Program, Branch, Year
    
    if not Program.objects.exists():
        programs = ['BCA', 'MCA', 'B.Tech', 'M.Tech', 'MBA']
        for prog in programs:
            Program.objects.create(program=prog)
            
    if not Branch.objects.exists():
        branches = ['Computer Science', 'Electronics', 'Mechanical', 'Civil']
        for branch in branches:
            Branch.objects.create(branch=branch)
            
    if not Year.objects.exists():
        years = ['1st Year', '2nd Year', '3rd Year', '4th Year']
        for year in years:
            Year.objects.create(year=year)


# ---------------------------
# Custom error handlers
# ---------------------------

def custom_404_view(request, exception):
    return render(request, "404.html", status=404)

# for resources file 
def resources(request):
    ns = News.objects.all()  # if you want to show news as in other pages
    return render(request, "resources.html", locals())

#for faqs 
def faqs(request):
    return render(request, 'faqs.html')
