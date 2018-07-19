from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from mongoengine import EmbeddedDocument, DynamicDocument, DynamicEmbeddedDocument
from mongoengine.fields import StringField, IntField, ListField, DecimalField, EmbeddedDocumentField, BooleanField

# Create your MySQL models here.
class Platforms(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    api_key = models.CharField(max_length=100)
     
     
class Reports(models.Model):
    report_id = models.AutoField(primary_key=True)
    platform = models.ForeignKey(Platforms, on_delete=models.CASCADE)
    report_name = models.CharField(max_length=50)
     
 
class Cases(models.Model):
    query_id = models.AutoField(primary_key=True)
    platform = models.ForeignKey(Platforms, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    creation_date = models.DateTimeField(auto_now_add=True)
    report_type = models.ForeignKey(Reports, on_delete=models.DO_NOTHING)
    query_title = models.CharField(max_length=100)
    status = models.CharField(max_length=10)


# Create your MongoDB models here.
class InputArgs(DynamicEmbeddedDocument):
    pass

class QueryInputs(DynamicDocument):
    lnkr_query_id = IntField()
    lnkr_user_id = IntField()
    platform = StringField()
    report_type = StringField()
    creation_date = DateTimeField(default=datetime.now())
    status = StringField()
    input_args = EmbeddedDocumentField(InputArgs, default=InputArgs())
    
class Price(EmbeddedDocument):
    CurrencyID = StringField(max_length=6)
    Value = DecimalField()

class EbayItem(DynamicDocument):
    lnkr_query_id = IntField()
    ItemID = StringField(max_length=16)
    Title = StringField()
    PaymentMethods = ListField(StringField())
    Site = StringField()
    QuantitySold = IntField()
#    CurrentPrice = EmbeddedDocumentField(Price)
#    ConvertedCurrentPrice = EmbeddedDocumentField(Price)
    HitCount = IntField()
    GlobalShipping = BooleanField()
    PrimaryCategoryID = StringField()
    PrimaryCategoryName = StringField()
    ListingType = StringField()
    PictureURL = ListField(StringField())
    ListingStatus = StringField()
    Country = StringField()
    Location = StringField()
    ListingType = StringField()

class EbaySellerDetails(DynamicDocument):
    lnkr_query_id = IntField()
    FeedbackScore = IntField()
    UserID = StringField()
    RegistrationSite = StringField(max_length=20)
    SellerBusinessType = StringField()
