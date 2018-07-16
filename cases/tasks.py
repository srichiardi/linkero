from celery import task
from mongoengine import connect
from django.core.mail import send_mail
from cases.ebayapi import EbayApi
from cases.models import EbayItem
import time


@task()
def send_ebay_listing_report(to_email, query_id=None):
    _MONGODB_USER = 'linkero-user'
    _MONGODB_PASSWD = '123linkero123'
    _MONGODB_HOST = 'localhost'
    _MONGODB_NAME = 'linkerodb'
    _MONGODB_PORT = 27017
    
    connect(_MONGODB_NAME, host=_MONGODB_HOST, port=_MONGODB_PORT, username=_MONGODB_USER, password=_MONGODB_PASSWD)
    
    ea = EbayApi()
    list_of_items = ['332094821083', '232698814292', '263757357723']
    time.sleep(10)
    j_items = ea.get_multiple_items(items_list=list_of_items)
    # assuming j_items['Ack'] == 'Success'
    for item in j_items['Item']:
        item['lnkr_query_id'] = query_id
        e_item = EbayItem(**item)
        e_item.save()
        
    itm = EbayItem.objects(ItemID="232698814292").first()
    item_title = itm.Title
    
    MSG_TEXT = 'Hi Stefano,\nyou pulled the item "{}"'.format(item_title)
    
    send_mail('Listings from Linkero', MSG_TEXT, 'LinkeroReports@linkero.ie', [to_email], fail_silently=False)
    