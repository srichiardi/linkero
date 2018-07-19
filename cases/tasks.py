import time
import json
from celery import task
from pandas import merge
from pandas.io.json import json_normalize
from mongoengine import connect
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from cases.ebayapi import EbayApi
from cases.models import EbayItem, QueryInputs, EbaySellerDetails, InputArgs, ApiErrorLog


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
                              input_args = InputArgs(**{ 'seller_id' : seller_id,
                                            'keywords' : keywords,
                                            'ebay_sites' : ebay_sites,
                                            'search_desc' : search_desc
                                            })
                              )
    
    query_input.save()
    
    ea = EbayApi()
    
    # search and pull unique list of items matching input criterias
    items_dict, slr_list, find_error_list = ea.find_items_multi_sites(e_sites=ebay_sites, kwd=keywords, s_id=seller_id, s_desc=search_desc)
    
    # pull item descriptions for each item
    ebay_item_list = ea.get_multi_items_threaded(items_dict)
    
    # add query_id to item dictionary before saving in MongoDB
    ebay_collection_list = []
    for item in ebay_item_list:
        item['lnkr_query_id'] = query_id
        ebay_collection_list.append(EbayItem(**item))
    # insert in bulk
    EbayItem.objects.insert(ebay_collection_list)
    
    # pull seller details
    seller_list = ea.get_multiple_sellers(seller_list=slr_list)
    seller_collection_list = []
    for slr in seller_list:
        slr['lnkr_query_id'] = query_id
        seller_collection_list.append(EbaySellerDetails(**slr))
    # insert in bulk
    EbaySellerDetails.objects.insert(seller_collection_list)
    
    # save api error messages
    error_collection_list = []
    if find_error_list:
        for err in find_error_list:
            err['lnkr_query_id'] = query_id
            error_collection_list.append(ApiErrorLog(**err))
        # insert in bulk
        ApiErrorLog.objects.insert(error_collection_list)
    
    # save the results in a CSV file and send it attached
    e_items = EbayItem.objects(lnkr_query_id=query_id)
    items_df = json_normalize(json.loads(e_items.to_json()))
    
    e_sellers = EbaySellerDetails.objects(lnkr_query_id=query_id)
    sellers_df = json_normalize(json.loads(e_sellers.to_json()))
    
    df = merge(items_df, sellers_df, left_on='Seller.UserID', right_on='UserID')
    
    file_name = "/home/stefano/linkero_ebay-listings_{}.csv".format(time.strftime("%Y%m%d-%H%M"))
    df.drop(['PictureURL', 'ViewItemURLForNaturalSearch'], axis=1)
    df.to_csv(file_name, sep='\t', encoding='utf-8', index=False)
    
    MSG_TEXT = 'Hi Stefano,\n\nplease find your query attached.\n\nthanks,\nLinkero'
    email = EmailMessage(
        'Linkero report: ebay listings',
        MSG_TEXT,
        'LinkeroReports@linkero.ie',
        [to_email]
    )
    file_attachment = open(file_name, 'r').read()
    email.attach('ebay_listing_output.csv', file_attachment, 'text/plain')
    email.send(fail_silently=False)
    file_attachment.close()
    
    # update status on mongoDB
    query_input.modify(status='completed')
    query_input.save()
    
    # delete the file from system
    
    