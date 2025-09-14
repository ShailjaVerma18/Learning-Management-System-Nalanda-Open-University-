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


# Forgot Password (Custom view to send email)
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                reverse('nouapp:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            send_mail(
                "Password Reset Request",
                f"Hi {user.username},\n\nClick the link below to reset your password:\n{reset_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('nouapp:login')
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")

    return render(request, "forgot_password.html")


# Reset Password (Custom view if you want your own template)
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password1")
            confirm_password = request.POST.get("new_password2")
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect("nouapp:login")
            else:
                messages.error(request, "Passwords do not match.")
        return render(request, "reset_password.html", {"validlink": True})
    else:
        messages.error(request, "Invalid or expired reset link.")
        return render(request, "reset_password.html", {"validlink": False})
