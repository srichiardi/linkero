import os
import time
import json
from csv import DictWriter
from io import StringIO
from celery import task
from pandas import merge
from pandas.io.json import json_normalize
from mongoengine import connect
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from cases.ebayapi import EbayApi
from cases.models import EbayItem, EbaySellerDetails, ApiErrorLog, CaseDetails


@task()
def send_ebay_listing_report(to_email, user_id=None, query_id=None, seller_id=None, keywords=None, ebay_sites=['US'], search_desc=False):

    # connect to Mongo
    mongo_client = connect('linkerodb', username='linkero-user', password='123linkero123')
        
    ea = EbayApi()
    
    #logger = send_ebay_listing_report.get_logger()
    
    #logger.info('starting find items')
    # search and pull unique list of items matching input criterias
    items_dict, slr_list, find_error_list = ea.find_items_multi_sites(e_sites=ebay_sites, kwd=keywords, s_id=seller_id, s_desc=search_desc)
    
    # check if find items search returned results
    if items_dict:
        #logger.info('starting items details')
        # pull item descriptions for each item
        ebay_item_list = ea.get_multi_items_threaded(items_dict, q_id=query_id)
        
        # pull seller details
        seller_list, seller_err_list = ea.get_multiple_sellers(seller_list=slr_list)
        seller_collection_list = []
        for slr in seller_list:
            slr['lnkr_query_id'] = query_id
            seller_collection_list.append(EbaySellerDetails(**slr))
        # insert in bulk
        EbaySellerDetails.objects.insert(seller_collection_list)
        #logger.info('saved seller details')
        
        # save api error messages
        find_error_list.extend(seller_err_list)
        error_collection_list = []
        if find_error_list:
            for err in find_error_list:
                err['lnkr_query_id'] = query_id
                error_collection_list.append(ApiErrorLog(**err))
            # insert in bulk
            ApiErrorLog.objects.insert(error_collection_list)
            #logger.info('saved error logs')
        
        # save the results in a CSV file and send it attached
        e_items = EbayItem.objects(lnkr_query_id=query_id)
        items_df = json_normalize(json.loads(e_items.to_json()))
        
        #e_sellers = EbaySellerDetails.objects(lnkr_query_id=query_id)
        sellers_df = json_normalize(seller_list)
        
        df = merge(items_df, sellers_df, left_on='Seller.UserID', right_on='UserID')
        
        filename = "linkero_ebay-listings_{}.csv".format(time.strftime("%Y%m%d-%H%M"))
        # to avoid key errors when a header is not in the dataframe
        headers = []
        main_headers = ["Seller.UserID", "ItemID", "ListingStatus", "Location", "Quantity", "QuantitySold", "CurrentPrice.Value",
                "CurrentPrice.CurrencyID", "Title", "GlobalShipping", "ShipToLocations",
                "BusinessSellerDetails.AdditionalContactInformation", "BusinessSellerDetails.Address.Street1", 
                "BusinessSellerDetails.Address.Street2", "BusinessSellerDetails.Address.CityName", 
                "BusinessSellerDetails.Address.StateOrProvince", "BusinessSellerDetails.Address.CountryName", 
                "BusinessSellerDetails.Address.Phone", "BusinessSellerDetails.Address.PostalCode", 
                "BusinessSellerDetails.Address.CompanyName", "BusinessSellerDetails.Address.FirstName", 
                "BusinessSellerDetails.Address.LastName", "BusinessSellerDetails.Email", "BusinessSellerDetails.LegalInvoice", 
                "BusinessSellerDetails.TradeRegistrationNumber", "BusinessSellerDetails.VATDetails.VATID", 
                "BusinessSellerDetails.VATDetails.VATPercent", "BusinessSellerDetails.VATDetails.VATSite", "Seller.FeedbackScore", 
                "Seller.PositiveFeedbackPercent", "UniquePositiveFeedbackCount", "UniqueNeutralFeedbackCount", "UniqueNegativeFeedbackCount"]
        df_headers = df.columns
        for hdr in main_headers:
            if hdr in df_headers:
                headers.append(hdr)
        df = df[headers]
        
        #df.to_csv(file_name, encoding='utf-8', index=False)
        #logger.info('created file')
        
        MSG_TEXT = 'Dear {},\n\nplease find the resuts from your query attached.\n\n\
thank you for using Linkero!'.format(User.objects.get(id=user_id).username)
        email = EmailMessage(
            'Linkero report: ebay listings',
            MSG_TEXT,
            'LinkeroReports@linkero.ie',
            [to_email]
        )
        file_attachment = StringIO()
        writer = DictWriter(file_attachment, fieldnames=headers)
        writer.writeheader()
        writer.writerows(df.to_dict('records'))
        file_attachment.seek(0)
        email.attach(filename, file_attachment.read(), 'text/csv')
        email.send(fail_silently=False)
        file_attachment.close()
        
        # delete the file from system
        query_status = 'completed'
        CaseDetails.objects(lnkr_query_id=query_id).update(set__file_name=filename)
    
    else:
        MSG_TEXT = 'Dear {},\n\nunfortunately your query returned zero results.\n\n\
thank you for using Linkero!'.format(User.objects.get(id=user_id).username)
        email = EmailMessage(
            'Linkero report: ebay listings',
            MSG_TEXT,
            'LinkeroReports@linkero.ie',
            [to_email]
        )
        email.send(fail_silently=False)
        query_status = 'zero results'
    
    # update status on mongoDB
    CaseDetails.objects(lnkr_query_id=query_id).update(set__status=query_status)
       
