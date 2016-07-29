# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Third Party Stuff
from django.db import models


class SignupModel(models.Model):

    ACCOUNT_TYPE = (
        ('Freemium', 'Freemium'),
        ('Starter', 'Starter'),
        ('Premium', 'Premium'),)
    name = models.CharField(
        blank=False, null=False, max_length=256)
    password = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(blank=False, null=False, max_length=15)
    company_name = models.CharField(blank=False, null=False, max_length=100)
    account_type = models.CharField(
        max_length=30, choices=ACCOUNT_TYPE, blank=False, null=False)

    def __str__(self):
        return self.name


class ConfirmSignup(models.Model):
    user = models.ForeignKey(SignupModel, on_delete=models.CASCADE)
    email_key = models.CharField(max_length=250)
    otp_key = models.CharField(max_length=250)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

    def __str__(self):
        return self.email_key
