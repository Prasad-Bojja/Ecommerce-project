from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, password):
        if not email:
            raise ValueError('Email address is required!!!')
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(name, email, password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    username=None
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.TextField(null=True, blank=True)
    mobile = models.IntegerField( null=True, blank=True,unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length = 100)
    created_at = models.DateTimeField(auto_now_add=True)

