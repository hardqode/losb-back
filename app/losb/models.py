from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db.models import CASCADE, PROTECT
from django.utils.translation import gettext_lazy as _
from django.db import models

from app import settings
from app.settings import SMS_VERIFICATOIN_CODE_DIGITS


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'

class SmsVerification(models.Model):
    code = models.CharField(max_length=settings.SMS_VERIFICATOIN_CODE_DIGITS)
    attempts = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class Phone(models.Model):
    code = models.PositiveSmallIntegerField()
    phone = models.PositiveSmallIntegerField(null=True, blank=True) #TODO: should it be charfield with regex validation?

    def __str__(self):
        return f'+{self.code}{self.phone if self.phone else '-not-verified'}'

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, telegram_id, password, **extra_fields):
        """
        Create and save a user with the given telegram_id and password.
        """
        if not telegram_id:
            raise ValueError(_("The telegram_id must be set"))
        phone = Phone.objects.create(code=7)
        user = self.model(telegram_id=telegram_id, phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, telegram_id, password, **extra_fields):
        """
        Create and save a SuperUser with the given telegram_id and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(telegram_id, password, **extra_fields)
    
    def get(self, *args, **kwargs):
        return super().select_related('phone', 'city').get(*args, **kwargs) #TODO: potentially add verification_code


class User(AbstractBaseUser, PermissionsMixin):
    telegram_id = models.CharField(max_length=255, unique=True)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    avatar = models.ImageField('Аватар', upload_to='user/avatar/', blank=True, null=True, max_length=512)
    phone = models.ForeignKey(Phone, on_delete=PROTECT,related_name='user')
    sms_verification = models.ForeignKey(SmsVerification, null=True, on_delete=PROTECT,related_name='user')
    password = models.CharField(max_length=255, blank=True, null=True)
    bday = models.DateField(null=True, default=None) # TODO: check naming Igor used
    city = models.ForeignKey(City, on_delete=PROTECT, related_name='user', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = None
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
