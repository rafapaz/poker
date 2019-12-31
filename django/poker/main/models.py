from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now


class MyUser(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    email = models.EmailField('Email', unique=True)
    money = models.IntegerField('Money', default=0)
    country = models.CharField('Country', max_length=255)
    token = models.CharField('Token', max_length=255, blank=True, null=True)
    time_zero = models.DateTimeField('Time with zero money', default=now)

    def __str__(self):
        return self.user.first_name