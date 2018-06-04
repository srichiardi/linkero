from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Case(models.Model):
    CASE_STATUS_CHOICES = (
        ( 'r' , 'running' ),
        ( 'c' , 'completed' ),
        ( 'f' , 'failed' ),
    )
    
    case_nr = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    platform = models.CharField(max_length=50, null=False, blank=False)
    query_text = models.CharField(max_length=50, null=False, blank=False)
    case_status = models.CharField(max_length=1, choices=CASE_STATUS_CHOICES)
    case_creation_dt = models.DateTimeField(auto_now_add=True)