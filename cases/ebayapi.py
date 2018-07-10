import pymongo
import requests
import json
from urllib.parse import urlencode


def connect_to_mongo():
    DB_NAME = "linkero-db"
    DB_HOST = "attila"
    DB_PORT = 27018
    DB_USER = "linkero-user"
    DB_PSWD = "123linkero123"
    return mongoengine.connect(DB_NAME, host=DB_HOST, port=DB_PORT, username=DB_USER, password=DB_PSWD)


class EbayApi():
    def __init__(self):
        self.api_key = 'StefanoR-ebayFric-PRD-19f17700d-ff298548'


    def load_find_items(self, ebay_site='EBAY-US', page_nr=1, keywords=None, seller_id=None, search_desc='false'):
    
        url_base = "http://svcs.ebay.com/services/search/FindingService/v1?"
    
        payload = { 'OPERATION-NAME' : 'findItemsAdvanced',
                     'SERVICE-VERSION' : '1.13.0',
                     'SECURITY-APPNAME' : self.api_key,
                     'RESPONSE-DATA-FORMAT' : 'JSON',
                     'GLOBAL-ID' : ebay_site,
                     'paginationInput.entriesPerPage' : 100,
                     'paginationInput.pageNumber' : page_nr,
                     'REST-PAYLOAD' : 'true' }
        
        if keywords:
            payload['keywords'] = keywords
        
        if seller_id:
            payload['itemFilter(0).name'] = 'Seller'
            payload['itemFilter(0).value'] = seller_id
        
        if search_desc:
            payload['descriptionSearch'] = search_desc
            
        url = url_base + urlencode(payload)        
        r = requests.get(url)        
        return json.loads(r.text)
        

    def get_multiple_items(self, items_list=[], site_id='0'):
        
        items_list_string = ','.join(items_list)
        
        url_base = "http://open.api.ebay.com/shopping?"
        
        payload = { 'appid' : self.api_key,
                'callname' : 'GetMultipleItems',
                'version' : '975',
                'responseencoding' : 'JSON',
                'ItemID' : items_list_string,
                'IncludeSelector' : 'Details',
                'siteid' : site_id }
        
        url = url_base + urlencode(payload)
        r = requests.get(url)
        return json.loads(r.text)


    def get_seller_details(self, seller_id):
        
        url_base = "http://open.api.ebay.com/shopping?"
        
        payload = { 'callname' : 'GetUserProfile',
                    'responseencoding' : 'JSON',
                    'appid' : self.api_key,
                    'version' : 967,
                    'IncludeSelector' : 'FeedbackHistory',
                    'UserID' : seller_id
                    }

        url = url_base + urlencode(payload)
        r = requests.get(url)
        return json.loads(r.text)
