from django.db import models
from django.contrib.auth.models import  AbstractBaseUser,PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

#models
from apps.common.models import ModelsBase
from apps.company.models import Company
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """ Crea y guarda el usuario con la contraseña proporcionada """
        
        if not username:
            raise ValueError('Debe ingresar el username')
        #username = self.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        #extra_fields.setdefault('is_superuser', False)
        #extra_fields.setdefault('last_login', now)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
            
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self._create_user(username, password, **extra_fields)
    
class User(AbstractBaseUser,PermissionsMixin,ModelsBase):
    username = models.CharField(max_length=40, unique=True)
    password = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, null=True)
    last_name = models.CharField(max_length=150, null=True)
    email = models.CharField(max_length=180, null=True)
    edad = models.IntegerField( null=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff =  models.BooleanField(default=False)
    company = models.ForeignKey(Company,on_delete=models.CASCADE, null=True)
    last_login = None
    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        db_table = 'User'
 