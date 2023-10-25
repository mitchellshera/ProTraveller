from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, phone_number=None):
        if not email:
            raise ValueError('The Email field is a must')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, phone_number=phone_number)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, phone_number=None):
        user = self.create_user(email, username, password, phone_number)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            validators.RegexValidator(
                regex=r'^\+[0-9]+$',
                message='Phone number must start with a "+" and contain only digits.',
                code='invalid_phone_number'
            )
        ]
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_users_permissions',
        related_query_name='custom_user_permission',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='authored_articles')
    images = models.ImageField(upload_to='article_images/', blank=True, null=True)
    cleanliness_rating = models.PositiveIntegerField(default=1, choices=[(i, i) for i in range(1, 6)])
    affordability_rating = models.PositiveIntegerField(default=1, choices=[(i, i) for i in range(1, 6)])
    service_rating = models.PositiveIntegerField(default=1, choices=[(i, i) for i in range(1, 6)])

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    points = models.IntegerField(default=0)
    saved = models.ManyToManyField('Article', related_name='saved_by', blank=True)

    def __str__(self):
        return self.user.username