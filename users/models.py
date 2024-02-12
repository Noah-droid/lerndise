from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover = models.ImageField(default=None, null=True, blank=True)
    outline =  models.TextField(default=None)
    
    # instructor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='courses_temp')  # Allow null temporarily


class CourseRequest(models.Model):
    # student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_requests')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    generated_content = models.TextField(blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
