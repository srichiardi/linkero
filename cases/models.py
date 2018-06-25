from django.db import models
from django.contrib.auth.models import User

class Platforms(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    api_key = models.CharField(max_length=100)
    
    
class Reports(models.Model):
    report_id = models.AutoField(primary_key=True)
    platform = models.ForeignKey(Platforms, on_delete=models.CASCADE)
    report_name = models.CharField(max_length=50)
    

# Create your models here.
class Cases(models.Model):
    QUERY_STATUS = (
        ('c', 'completed'),
        ('f', 'failed'),
        ('r', 'running'),
    )
    query_id = models.AutoField(primary_key=True)
    platform = models.ForeignKey(Platforms, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    creation_date = models.DateTimeField(auto_now_add=True)
    report_type = models.ForeignKey(Reports, on_delete=models.DO_NOTHING)
    query_title = models.CharField(max_length=100)
    status = models.CharField(max_length=1, choices=QUERY_STATUS)
    