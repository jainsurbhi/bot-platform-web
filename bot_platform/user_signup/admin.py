# Third Party Stuff
from django.contrib import admin

from .models import SignupModel, ConfirmSignup

# Register your models here.
admin.site.register(SignupModel)
admin.site.register(ConfirmSignup)
