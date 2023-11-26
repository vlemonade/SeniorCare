from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class senior_list(models.Model):
  first_name= models.CharField(max_length=20,null=True)
  last_name= models.CharField(max_length=20)
  middle_name= models.CharField(max_length=20)
  suffix= models.CharField(max_length=5, null=True)
  age= models.BigIntegerField(null=True)
  
  SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
  sex = models.CharField(max_length=10, choices=SEX_CHOICES, null=True)
  birth_date= models.DateField(null=True)
  address= models.CharField(max_length=100, null=True)
  phone_number= models.CharField(max_length=12, null=True)
  OSCA_ID= models.CharField(max_length=20, null=True)
  updated = models.DateTimeField(auto_now=True)
  created=models.DateTimeField(auto_now_add=True)
  is_claimed = models.BooleanField(default=False)
  claimed_date = models.DateTimeField(null=True, blank=True)
  senior_image = models.ImageField(upload_to='media/', blank=True, null=True)
  proof_of_claiming = models.ImageField(upload_to='proof/', blank=True, null=True)
  status = models.BooleanField(default=True)
  active_status = models.CharField(max_length=20, default='active', null=True)

  def is_active(self):
        return self.status and (timezone.now() - self.created).days <= 30
  
  def __str__(self):
        return f"{self.first_name} "

class SMSMessage(models.Model):
    from_number = models.CharField(max_length=15)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_number}: {self.body}"
    

