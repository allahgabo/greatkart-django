from django.shortcuts import render,redirect
from .forms import RegistraionForm
from .models import  Account
from django.contrib import  messages,auth
from django.contrib.auth.decorators import  login_required

# verifcation email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage



def register(request):
	if request.method=='POST':
		form=RegistraionForm(request.POST)
		if form.is_valid():
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			phone_number=form.cleaned_data['phone_number']
			email=form.cleaned_data['email']
			password=form.cleaned_data['password']
			username=email.split('@')[0]
			user=Account.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
			user.phone_number=phone_number
			user.save()
			# activation email
			current_site=get_current_site(request)
			mail_subject='Please activate your account'
			message=render_to_string('accounts/account_verifecation_mail.html',{
				'user':user,
				'domain': current_site,
				'uid':urlsafe_base64_encode(force_bytes(user.pk)),
				'token': default_token_generator.make_token(user),
				}
				)
			to_mail=email
			send_mail=EmailMessage(mail_subject,message,to=[to_mail])
			send_mail.send()
			#messages.success(request,'You have Register successfully ')
			return redirect('/accounts/login/?command=verification&email='+email)
	else:
		form=RegistraionForm()

	context={
		'form':form,
	}
	return render(request,'accounts/register.html',context)

def login(request):
	if request.method =='POST':
		email=request.POST['email']
		password=request.POST['password']
		user=auth.authenticate(email=email,password=password)
		if user is not None:
			auth.login(request,user)
			messages.success(request,'You Logged In..')
			return redirect('dashboard')
		else:
			messages.error(request,'Invalid login Data')
			return redirect('login')
	return render(request,'accounts/login.html')


@login_required(login_url='login')
def logout(request):
	auth.logout(request)
	messages.success(request,'You Logged Out successfully')
	return redirect('login')
	return render(request,'accounts/logout.html')


def activate(request,uidb64,token):
	try:
		uid=urlsafe_base64_decode(uidb64).decode()
		user=Account._default_manager.get(pk=uid)
	except (TypeError,ValueError,OverflowError,Account.DoesNotExist):
		user=None
	if user is not None and default_token_generator.check_token(user, token):
		user.is_active = True
		user.save()
		message.success(request,'Congratulation your activation is successfully')
		return redirect('login')
	else:
		message.error(request,'Invalid mail Token')
		return redirect('register')
	

@login_required(login_url='login')
def dashboard(request):
	return render(request,'accounts/dashboard.html')



def forgotpassword(request):
	if request.method=='POST':
		email=request.POST['email']
		if Account.objects.filter(email=email).exists():
			user=Account.objects.get(email__exact=email)
			#Reset Password
			current_site=get_current_site(request)
			mail_subject='Reset Your Password'
			message=render_to_string('accounts/reset_password_email.html',{
				'user':user,
				'domain': current_site,
				'uid':urlsafe_base64_encode(force_bytes(user.pk)),
				'token': default_token_generator.make_token(user),
				})
			to_mail=email
			send_mail=EmailMessage(mail_subject,message,to=[to_mail])
			send_mail.send()
			messages.success(request,'Password Reset emaill has sent to your emaill')
			return redirect('login')
		else:
			messages.error(request,'Account does not exist')
			return redirect('register')
	return render(request,'accounts/forgotpassword.html')


def resetpassword_validate(request,uidb64,token):
	try:
		uid=urlsafe_base64_decode(uidb64).decode()
		user=Account._default_manager.get(pk=uid)
	except (TypeError,ValueError,OverflowError,Account.DoesNotExist):
		user=None
	if user is not None and default_token_generator.check_token(user, token):
		request.session['uid']=uid
		messages.success(request,'please reset your password')
		return redirect('resetpassword')
	else:
		messages.error(request,'This link has been explired')
		return redirect('login')

	return redirect('login')

def resetpassword(request):
	if request.method == 'POST':
		password=request.POST['password']
		confirmpassword=request.POST['confirmpassword']
		if password == confirmpassword:
			uid=request.session.get('uid')
			user=Account.objects.get(pk=uid)
			user.set_password(password)
			user.save()
			messages.success(request,'Password reset successfully')
			return redirect('login')
		else:
			messages.error(request,'password dont match')
			return redirect('resetpassword')
	else:
		return render(request,'accounts/resetpassword.html')