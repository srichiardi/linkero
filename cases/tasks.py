from celery import task
from django.core.mail import send_mail
from cases.ebayapi import EbayApi
from cases.models import EbayItem
import time


@task()
def send_ebay_listing_report(to_email, query_id=None):
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
    
    send_mail('Listings from Linkero', MSG_TEXT, 'LinkeroReports@linkero.ie', ['s.richiardi@gmail.com'], fail_silently=False)
    