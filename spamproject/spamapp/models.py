from django.db import models

# Create your models here.


# User registering model
class User(models.Model):
    name=models.CharField(max_length=255,null=False)
    phone_number=models.CharField(max_length=15,unique=True,null=False)
    email=models.CharField(max_length=255,unique=True,null=True)
    password=models.CharField(max_length=200)

# Users can create their contacts
class Contact(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    contact_name = models.CharField(max_length=255,null=False)
    contact_phone_number = models.CharField(max_length=15,null=False)
    

# Users can mark spam
class SpamReport(models.Model):
    phone_number = models.CharField(max_length=15, null=False)
    is_spam = models.BooleanField(default=True)
    # count_spam_hits = models.IntegerField(default=0)









