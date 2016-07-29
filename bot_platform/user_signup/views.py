# -*- coding: utf-8 -*-
import datetime

import hashlib

import random

from django.http import HttpResponseRedirect

from django.shortcuts import get_object_or_404, render, render_to_response

from django.utils import timezone

from django.views.generic import View

import requests

from .forms import SignupModelForm

from .models import ConfirmSignup

from ..users.models import User


class SignupFormView(View):

    def generate_email(self, user):
        datas = {}
        datas['username'] = user.username
        datas['email'] = user.email
        datas['password'] = user.password

        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        usernamesalt = datas['username']
        if isinstance(usernamesalt, unicode):
            usernamesalt = usernamesalt.encode('utf8')
        datas['activation_key'] = hashlib.sha1(salt + usernamesalt).hexdigest()

        datas['email_path'] = "/ActivationEmail.txt"
        datas['email_subject'] = "Activation Link for"

        SignupModelForm.sendEmail(datas)
        SignupModelForm.saving(datas)
        request.session['registered'] = True
        return True

    def generate_OTP_pin(self, user):
        key = random.randint(1231231213, 99999999999999)
        ConfirmSignup.objects.get_or_create(
            user=user, otp_key=key)
        return True
        # To-Do Code Clean-Up
        # To Invoke this function on more than one try and update the key

    def get(self, request, format=None):
        template_name = 'signup.html'
        context = {'form': SignupModelForm}
        return render(request, template_name, context)

    def post(self, request, format=None):

        form = SignupModelForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            user = User.objects.create_user(
                instance.email, password=instance.password, first_name=instance.name)
            instance.save()
            self.generate_OTP_pin(instance)
            self.generate_email(instance)
            user.save()

            return HttpResponseRedirect('/confirmkey/')
        else:
            form = SignupModelForm()

        render_to_response(
            'signup.html', {'form': SignupModelForm})

    def activation(self, request, key):
        activation_expired = False
        already_active = False
        profil = get_object_or_404(ConfirmSignup, activation_key=key)
        if profil.user.is_active is False:
            if timezone.now() > profil.key_expires:
                activation_expired = True
                id_user = profil.user.id
            else:
                profil.user.is_active = True
                profil.user.save()

        else:
            already_active = True
        return render(request, '.html', locals())

    def new_activation_link(self, request, user_id):
        form = SignupModelForm()
        datas = {}
        user = User.objects.get(id=user_id)
        if user is not None and not user.is_active:
            datas['username'] = user.username
            datas['email'] = user.email
            datas['email_path'] = "/ResendEmail.txt"
            datas['email_subject'] = "Activation Link for"

            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            usernamesalt = datas['username']
            if isinstance(usernamesalt, unicode):
                usernamesalt = usernamesalt.encode('utf8')
            datas['activation_key'] = hashlib.sha1(salt + usernamesalt).hexdigest()

            profil = ConfirmSignup.objects.get(user=user)
            profil.activation_key = datas['activation_key']
            profil.key_expires = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")
            profil.save()

            form.sendEmail(datas)
            request.session['new_link'] = True

        return HttpResponseRedirect('/')


class ConfirmKeyView(View):

    def get(self, request, format=None):
        template_name = 'confirmkey.html'
        return render(request, template_name)

    def post(self, request, format=None):
        entered_key = request.POST['key']
        try:
            valid_key = ConfirmSignup.objects.get(email_key=entered_key)
            if entered_key == valid_key.email_key:
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/signup/')
        except:
            return HttpResponseRedirect('/signup/')

