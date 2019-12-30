from django.db import models
from django.contrib.auth import get_user_model


class MyUser(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    email = models.EmailField('Email', unique=True)
    money = models.DecimalField('Money', max_digits=16, decimal_places=2, default=0)
    country = models.CharField('Country', max_length=255)

    def __str__(self):
        return self.user.first_name