from django.contrib.auth import login, authenticate
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from accounts.models import Profile
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token
from django.template.loader import render_to_string

from .forms import SignUpForm
from .tokens import account_activation_token

import requests

def home_view(request):
    return render(request, 'accounts/home.html')


def profile_view(request):
    username = request.user.username
    email = request.user.email
    confirmation = request.user.profile.signup_confirmation

    context = {'username': username, 'email': email, 'confirmation': confirmation}
    return render(request, 'accounts/profile.html', context)


def activation_sent_view(request):
    return render(request, 'accounts/activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.signup_confirmation = True
        user.save()
        login(request, user)
        return redirect('profile')
    else:
        return render(request, 'accounts/activation_invalid.html')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')

            api_key = '8d7e1b7f-022b-4bf5-8661-ac2f949a1a1c'   # With an API key you wont be limited by how many addresses you can check
                                                               # To get the  API key you need to signup in Real Email API website: https://isitarealemail.com/register
                                                               # i have signedin from my 'dipen.stha8786@gmail.com' email address
                                                               # IMP_NOTE: if you are not signed in user and u don't have API Key then also you can use this Real Email API .. But there is limitation without API Key as you can  only test for 100 emails per day

            response = requests.get(
                "https://isitarealemail.com/api/email/validate",  # API ko end point
                params={'email': email},                                        # hamro email as a params pathauna parcha
                headers={'Authorization': "Bearer " + api_key})                 # API key lai chai headers vanni field ma 'Authorization' as a headers send garna parcha

            status = response.json()['status']  # response ma ayeko kura lai json ma lageko
                                                # email valid cha vani status ma 'valid' response auncha else 'invalid' auncha ..
                                                # yedi user le jpt domain vako email eg: aaaa@bbb.com yesto diyo vani 'unknown' response auncha becz yo email bata kei tha hunaa becz mail server ko name nai jpt diyeko cha

           
            print(status)
            if status == "valid":
                user = form.save()
                user.refresh_from_db()
                user.profile.first_name = form.cleaned_data.get('first_name')
                user.profile.last_name = form.cleaned_data.get('last_name')
                user.profile.email = form.cleaned_data.get('email')
                user.is_active = False
                user.save()

                
                current_site = get_current_site(request)
                subject = 'Please Activate Your Account'
                message = render_to_string('accounts/activation_request.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)  # email_user() djanog le diyeko inbuilt method ho ...  # email send garna django le arko method pani deko cha i.e send_mail()
                return redirect('activation_sent')

            else:
                return HttpResponse("Email address you provided does not exist ! Please provide a valid email address.")


    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})
