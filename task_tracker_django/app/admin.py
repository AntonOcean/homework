from django.contrib import admin
from app.models import Task, User

admin.site.register(User)
admin.site.register(Task)