import json
from threading import Thread
from queue import Queue
from celery import task
from mongoengine import connect
from django.core.mail import send_mail
from cases.ebayapi import EbayApi
from cases.models import EbayItem, QueryInputs


@task()
def send_ebay_listing_report(to_email, user_id=None, query_id=None, seller_id=None, keywords=None, ebay_sites=['US'], search_desc=False):
    # connect to Mongo
    _MONGODB_USER = 'linkero-user'
    _MONGODB_PASSWD = '123linkero123'
    _MONGODB_HOST = 'localhost'
    _MONGODB_NAME = 'linkerodb'
    _MONGODB_PORT = 27017
    connect(_MONGODB_NAME, host=_MONGODB_HOST, port=_MONGODB_PORT, username=_MONGODB_USER, password=_MONGODB_PASSWD)
    
    query_input = QueryInputs(lnkr_query_id = query_id,
                              lnkr_user_id = user_id,
                              platform = 'ebay',
                              report_type = 'listing details',
                              status = 'running',
                              input_args = { 'seller_id' : seller_id,
                                            'keywords' : keywords,
                                            'ebay_sites' : ebay_sites,
                                            'search_desc' : search_desc
                                            }
                              )
    
    query_input.save()
    
    ea = EbayApi()
    
    # create find item queue:
    find_item_queue = Queue()
    

    list_of_items = ['332094821083', '232698814292', '263757357723']

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
    