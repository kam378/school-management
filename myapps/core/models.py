from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


# Create your models here.
# class School(models.Model):
#     name = models.CharField(max_length=100)
#     subdomain = models.SlugField(max_length=50, unique=True, help_text="Unique identifier for the school (e.g., 'st-marys')")
#     address = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} Notiification for user {self.user.username}"