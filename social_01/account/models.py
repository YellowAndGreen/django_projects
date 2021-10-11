from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


# 使用settings.AUTH_USER_MODEL会报错，实际无影响，改为"auth.User"效果一样且不报错
class Profile(models.Model):
    user = models.OneToOneField("auth.User",
                                on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/',
                              blank=True)

    def __str__(self):
        return f'Profile for user {self.user.username}'

