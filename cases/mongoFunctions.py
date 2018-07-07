import mongoengine
import requests
import json

def connect_to_mongo():
    DB_NAME = "linkero-db"
    DB_HOST = "attila"
    DB_PORT = 27018
    DB_USER = "linkero-user"
    DB_PSWD = "123linkero123"
    return mongoengine.connect(DB_NAME, host=DB_HOST, port=DB_PORT, username=DB_USER, password=DB_PSWD)

def load_find_items(ebay_site='US', page_nr=1, keywords=None, seller_id=None, search_desc='false'):

    find_items_url = "http://svcs.ebay.com/services/search/FindingService/v1?"

    payload = { 'OPERATION-NAME' : 'findItemsAdvanced',
                 'SERVICE-VERSION' : '1.13.0',
                 'SECURITY-APPNAME' : 'StefanoR-ebayFric-PRD-19f17700d-ff298548',
                 'RESPONSE-DATA-FORMAT' : 'JSON',
                 'GLOBAL-ID' : site,
                 'paginationInput.entriesPerPage' : 100,
                 'paginationInput.pageNumber' : page_nr,
                 'REST-PAYLOAD' : 'true' }
    
    if keywords:
        payload['keywords'] = keywords
    
    if seller_id:
        payload['itemFilter(0).name'] = 'Seller'
        payload['itemFilter(0).value'] = searchOptions['sellerId']
    
    if search_desc:
        payload['descriptionSearch'] = search_desc
        
    r = requests.get(url)
    
    return json.loads(r.text)
        

def get_multiple_items(items_list=[], site_id='0'):
    items_list_string = ','.join(items_list)
    ebayShoppingUrl = "http://open.api.ebay.com/shopping?"
    esPayload = { 'appid' : 'StefanoR-ebayFric-PRD-19f17700d-ff298548',
            'callname' : 'GetMultipleItems',
            'version' : '975',
            'responseencoding' : 'JSON',
            'ItemID' : items_list_string,
            'IncludeSelector' : 'Details',
            'siteid' : site_id }
    
    url = ebayShoppingUrl + urlencode(esPayload)
    r = requests.get(url)
    return json.loads(r.text)


def get_seller_details(seller_id):
    url_templ = "http://open.api.ebay.com/shopping?\
callname=GetUserProfile&\
responseencoding=JSON&\
appid=StefanoR-ebayFric-PRD-19f17700d-ff298548&\
version=967&\
IncludeSelector=FeedbackHistory&\
UserID={}"
    url = url_templ.format(seller_id)
    r = requests.get(url)
    return json.loads(r.text)

