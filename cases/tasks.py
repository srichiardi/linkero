import json
from collections import defaultdict
from celery import task
from mongoengine import connect
from django.core.mail import send_mail
from cases.ebayapi import EbayApi
from cases.models import EbayItem, QueryInputs, EbaySellerDetails


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
    
    # search and pull unique list of items matching input criterias
    items_dict, slr_list = ea.find_items_multi_sites(e_site=ebay_sites, kwd=keywords, s_id=seller_id, s_desc=search_desc)
    
    # pull item descriptions for each item
    ebay_item_list = ea.get_multi_items_threaded(items_dict)
    
    # add query_id to item dictionary before saving in MongoDB
    for item in j_items['Item']:
        item['lnkr_query_id'] = query_id
        ebay_item_list.append(EbayItem(**item))
    # insert in bulk
    EbayItem.objects.insert(ebay_item_list)
    
    # pull seller details
    seller_list = ea.get_multiple_sellers(seller_list=slr_list)
    
    # pull all results and tabulate
    
    
    MSG_TEXT = 'Hi Stefano,\nyou pulled the item "{}"'.format(item_title)
    
    send_mail('Linkero report: ebay listings', MSG_TEXT, 'LinkeroReports@linkero.ie', [to_email], fail_silently=False)
    