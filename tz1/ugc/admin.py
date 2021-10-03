from django.contrib import admin

from .forms import ProfileForm
from .models import Profile, Questionnaire


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'name')
    form = ProfileForm


@admin.register(Questionnaire)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'login_telegram', 'reply_1', 'reply_2', 'reply_3')
