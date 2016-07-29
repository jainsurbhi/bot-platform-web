
# -*- coding: utf-8 -*-
import datetime

from django import forms

from django.conf import settings

from django.core.mail import send_mail

from django.template import Context, Template

from .models import ConfirmSignup, SignupModel


class SignupModelForm(forms.ModelForm):

    class Meta:
        model = SignupModel
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(),
        }

    def saving(self, datas):
        u = SignupModel.objects.create_user(datas['name'], datas['email'], datas['password'])
        u.is_active = False
        u.save()
        profil = ConfirmSignup()
        profil.user = u
        profil.activation_key = datas['activation_key']
        profil.key_expires = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")
        profil.save()
        return u

    def sendemail(self, datas):
        link = "http://yourdomain.com/activate/" + datas['activation_key']
        c = Context({'activation_link': link, 'username': datas['username']})
        f = open(common.MEDIA_ROOT + datas['email_path'], 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        send_mail(datas['email_subject'], message, 'yourdomain <no-reply@yourdomain.com>', [datas['email']], fail_silently=False)