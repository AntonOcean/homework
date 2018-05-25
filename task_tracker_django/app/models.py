from django.contrib.auth.models import AbstractUser
from django.db import models
from task_tracker_django import settings

STATUS_CHOICES = (
    ('new_task', 'new_task'),
    ('in_work', 'in_work'),
    ('done', 'done')
)


class Task(models.Model):
    title = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new_task', null=True, blank=True)
    text = models.CharField(max_length=255, null=True, blank=True)
    parent_task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    def childrens(self):
        childs = Task.objects.filter(parent_task=self.id)
        return childs


class User(AbstractUser):
    pass