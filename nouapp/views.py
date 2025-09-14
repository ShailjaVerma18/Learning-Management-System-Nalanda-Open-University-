from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import date

from .models import Enquiry, Student, Login
from adminapp.models import Program, Branch, Year, News
from . import smssender

# Custom 404 Error Page
def custom_404(request, exception):
    """
    Custom 404 error page view
    """
    return render(request, '404.html', status=404)

# Theme toggle
@require_POST
def set_theme(request):
    theme = request.POST.get('theme', 'light')
    request.session['theme'] = theme
    return JsonResponse({'status': 'ok'})

# Home & Info Pages
def index(request):
    ns = News.objects.all()
    return render(request, "index.html", {'ns': ns})

def aboutus(request):
    ns = News.objects.all()
    return render(request, "aboutus.html", {'ns': ns})

def courses(request):
    return render(request, "courses.html")

def services(request):
    return render(request, "services.html")

# Registration
def registration(request):
    ns = News.objects.all()
    program = Program.objects.all()
    branch = Branch.objects.all()
    year = Year.objects.all()

    if request.method == "POST":
        rollno = request.POST['rollno']
        name = request.POST['name']
        fname = request.POST['fatherName']
        mname = request.POST['motherName']
        gender = request.POST['gender']
        address = request.POST['address']
        program_sel = request.POST['program']
        branch_sel = request.POST['branch']
        year_sel = request.POST['year']
        contactno = request.POST['contactNo']
        emailaddress = request.POST['emailAddress']
        password = request.POST['password']
        regdate = date.today()
        usertype = 'student'
        status = 'false'

        stu = Student(
            rollno=rollno, name=name, fname=fname, mname=mname, gender=gender,
            address=address, program=program_sel, branch=branch_sel,
            year=year_sel, contactno=contactno, emailaddress=emailaddress,
            regdate=regdate
        )
        log = Login(userid=rollno, password=password, usertype=usertype, status=status)
        stu.save()
        log.save()
        messages.success(request, 'Your Registration is submitted successfully.')

    return render(request, "registration.html", {
        'ns': ns,
        'program': program,
        'branch': branch,
        'year': year
    })

# Login
def login(request):
    ns = News.objects.all()
    if request.method == "POST":
        userid = request.POST['userid']
        password = request.POST['password']
        try:
            obj = Login.objects.get(userid=userid, password=password)
            if obj.usertype == "student":
                request.session['rollno'] = userid
                return redirect(reverse('studentapp:studenthome'))
            elif obj.usertype == "admin":
                request.session['adminid'] = userid
                return redirect(reverse('adminapp:adminhome'))
        except Login.DoesNotExist:
            messages.error(request, 'Invalid user credentials.')

    return render(request, "login.html", {'ns': ns})

# Contact
def contactus(request):
    ns = News.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        gender = request.POST['gender']
        address = request.POST['address']
        contactno = request.POST['contactno']
        emailaddress = request.POST['emailaddress']
        enquirytext = request.POST['enquirytext']
        enquirydate = date.today()

        enq = Enquiry(
            name=name, gender=gender, address=address,
            contactno=contactno, emailaddress=emailaddress,
            enquirytext=enquirytext, enquirydate=enquirydate
        )
        enq.save()
        # smssender.sendsms(contactno)
        messages.success(request, 'Your Enquiry is submitted successfully.')

    return render(request, "contactus.html", {'ns': ns})
