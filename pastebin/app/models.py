import hashlib
import os
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Поле email должно быть заполнено")
        
        email = self.normalize_email(email)
        
        existing_user = self.model.objects.filter(email=email).first()
        if existing_user:
            for key, value in extra_fields.items():
                setattr(existing_user, key, value)
            existing_user.save(using=self._db)
            return existing_user
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, verbose_name='именем', unique=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.email
    

class Paste(models.Model):
    author = models.ForeignKey(CustomUser, related_name='pastes', on_delete=models.SET_NULL,
                                null=True, blank=True, verbose_name='Автор')
    content = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True)
    unique_hash = models.CharField(max_length=64, unique=True) # для создания уникальной ссылки
    expiration_time = models.DurationField(default=timedelta(hours=1),
                                            verbose_name='Через какое время удалить') 
    password = models.CharField(max_length=8, null=True, blank=True, verbose_name='Пароль')
    
    def generate_unique_hash(self):
        while True:
            unique_string = f"{self.content}{os.urandom(16)}"
            new_hash = hashlib.sha256(unique_string.encode()).hexdigest()
            if not Paste.objects.filter(unique_hash=new_hash).exists():
                return new_hash

    def save(self, *args, **kwargs):
        if not self.unique_hash: 
            self.unique_hash = self.generate_unique_hash()
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.created_at + self.expiration_time

    def time_to_expire(self):
        time_delta = self.created_at + self.expiration_time - timezone.now() 
        total_seconds = int(time_delta.total_seconds())
        
        # Определяем количество месяцев, дней, часов и минут
        months = total_seconds // (30 * 24 * 3600) 
        days = (total_seconds % (30 * 24 * 3600)) // (24 * 3600)
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % 3600) // 60

        time_parts = []
        if months > 0:
            time_parts.append(f"{months}м")
        if days > 0:
            time_parts.append(f"{days}д")
        if hours > 0:
            time_parts.append(f"{hours}ч")
        if minutes > 0:
            time_parts.append(f"{minutes}мин")

        if not time_parts:
            return "0мин"

        return " ".join(time_parts)
   

    def __str__(self):
        return self.unique_hash
    