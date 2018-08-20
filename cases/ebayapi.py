import requests
import json
from threading import Thread
from queue import Queue
from urllib.parse import urlencode
from collections import defaultdict
from cases.ebaySettings import globalSiteMap
from cases.models import EbayItem
from mongoengine import connect


class EbayApiException(Exception):
    pass


class EbayApi():
    def __init__(self):
        self.api_key = 'StefanoR-ebayFric-PRD-19f17700d-ff298548'
        # connect to Mongo
        _MONGODB_USER = 'linkero-user'
        _MONGODB_PASSWD = '123linkero123'
        _MONGODB_HOST = 'localhost'
        _MONGODB_NAME = 'linkerodb'
        _MONGODB_PORT = 27017
        self.conn = connect(_MONGODB_NAME, host=_MONGODB_HOST, port=_MONGODB_PORT, username=_MONGODB_USER, password=_MONGODB_PASSWD)   


    def find_items(self, ebay_site='US', page_nr=1, keywords=None, seller_id=None, search_desc=None):
    
        url_base = "http://svcs.ebay.com/services/search/FindingService/v1?"
    
        payload = { 'OPERATION-NAME' : 'findItemsAdvanced',
                     'SERVICE-VERSION' : '1.13.0',
                     'SECURITY-APPNAME' : self.api_key,
                     'RESPONSE-DATA-FORMAT' : 'JSON',
                     'GLOBAL-ID' : globalSiteMap[ebay_site]['globalID'],
                     'paginationInput.entriesPerPage' : 100,
                     'paginationInput.pageNumber' : page_nr,
                     'REST-PAYLOAD' : 'true',
                     'outputSelector' : 'SellerInfo' }
        
        if keywords:
            payload['keywords'] = keywords
        
        if seller_id:
            payload['itemFilter(0).name'] = 'Seller'
            payload['itemFilter(0).value'] = seller_id
        
        if search_desc:
            payload['descriptionSearch'] = 'true'
            
        url = url_base + urlencode(payload)        
        r = requests.get(url)
        
        j_results = json.loads(r.text)
         
        if j_results['findItemsAdvancedResponse'][0]['ack'][0] == 'Success':
            return json.loads(r.text)
        else:
            ERR_MSG = {'platform' : 'ebay',
                       'api_call' : 'findItemsAdvanced',
                       'input' : 'ebay_site: {}, page_nr: {}, keywords: {}, seller_id: {}, search_desc: {}'.format(ebay_site, page_nr, keywords, seller_id, search_desc),
                       'error_message' :  j_results['findItemsAdvancedResponse'][0]['errorMessage'][0]['error'][0]['message'][0]}
            raise EbayApiException(ERR_MSG)
    
        
    def find_items_multi_pages(self, out_q=None, err_q=None, e_site='US', kwd=None, s_id=None, s_desc=None):
        """ pull results of advanced search and return dictionary with items id for keys and seller id,
        site id as values """
        tot_pages = 1
        page = 1
        
        while page <= min(100, tot_pages):
            
            try:
                result_set = self.find_items(ebay_site = e_site, page_nr = page, keywords = kwd, seller_id = s_id,
                                    search_desc = s_desc)
            except EbayApiException as e:
                err_q.put(e.args[0])
                break
            else:
                tot_pages = int(result_set['findItemsAdvancedResponse'][0]['paginationOutput'][0]['totalPages'][0])
                page += 1
                
                results_count = int(result_set['findItemsAdvancedResponse'][0]['searchResult'][0]['@count'])
                if results_count > 0:
                    items_dict = defaultdict(dict)
                    for item in result_set['findItemsAdvancedResponse'][0]['searchResult'][0]['item']:
                        items_dict[item['itemId'][0]]['sellerUserName'] = item['sellerInfo'][0]['sellerUserName'][0]
                        items_dict[item['itemId'][0]]['ebaySite'] = e_site
                    
                    out_q.put(items_dict)
    
    
    def find_items_multi_sites(self, e_sites=['US'], kwd=None, s_id=None, s_desc=None):
        """ Start up to 20 parallel threads, one each site id """
        threads_list = []
        out_queue = Queue()
        err_queue = Queue()
        for site in e_sites:
            thread_call = Thread(target = self.find_items_multi_pages,
                                 kwargs = {'out_q' : out_queue,
                                           'err_q' : err_queue,
                                           'e_site' : site,
                                           'kwd' : kwd,
                                           's_id' : s_id,
                                           's_desc' : s_desc}
                                 )
            threads_list.append(thread_call)
            thread_call.start()
            
        # wait for threads to finish
        for t in threads_list:
            t.join()
        
        # fill dict with item id as key and list of sites as values
        items_dict = defaultdict(list)
        seller_list = []
        error_list = []
        while not out_queue.empty():
            batch = out_queue.get()
            for item, i_dict in batch.items():
                site = i_dict['ebaySite']
                seller = i_dict['sellerUserName']
                if site not in items_dict[item]:
                    items_dict[item].append(site)
                if seller not in seller_list and seller != '':
                    seller_list.append(seller)
                
            out_queue.task_done()
        
        while not err_queue.empty():
            error_list.append(err_queue.get())            
            
        return items_dict, seller_list, error_list
            

    def get_multiple_items(self, out_q=None, items_list=[], ebay_site='US'):
        
        items_list_string = ','.join(items_list)
        
        url_base = "http://open.api.ebay.com/shopping?"
        
        payload = { 'appid' : self.api_key,
                'callname' : 'GetMultipleItems',
                'version' : '975',
                'responseencoding' : 'JSON',
                'ItemID' : items_list_string,
                'IncludeSelector' : 'Details',
                'siteid' : globalSiteMap[ebay_site]['siteID'] }
        
        url = url_base + urlencode(payload)
        r = requests.get(url)
        
        if out_q:
            out_q.put(json.loads(r.text))
        else:
            return json.loads(r.text)
        
        
    def get_multi_items_threaded(self, items_dict={}, max_threads=20, q_id=None):
        # generating a dict sites with lists of items
        sites_priority = ('GB', 'US', 'IE', 'CA-EN', 'AU', 'IT', 'FR', 'CA-FR', 'ES', 'AT', 'BE-FR', 'DE', 'MOTOR', 'BE-NL', 'NL', 'CH', 'HK', 'IN', 'MY', 'PH', 'PL', 'SG')
        items_by_sites = defaultdict(list)
        for item_id, e_sites in items_dict.items():
            for p_site in sites_priority:
                if p_site in e_sites:
                    items_by_sites[p_site].append(item_id)
                    break
        
        output_queue = Queue()
        for site, items in items_by_sites.items():
            item_packets = [ items[i:i+20] for i in range(0, len(items), 20) ]
            threads_list = []
            # batches of 20 packets of 20 items  
            items_matrix = [ item_packets[i:i+max_threads] for i in range(0, len(item_packets), max_threads) ]
            for batch in items_matrix:
                for string_list in batch:
                    thread_call = Thread(target=self.get_multiple_items,
                                         kwargs={ 'out_q' : output_queue,
                                                 'items_list' : string_list,
                                                 'ebay_site' : site
                                             }
                                         )
                    threads_list.append(thread_call)
                    thread_call.start()
                for t in threads_list:
                    t.join()
                
                items_results = []
                while not output_queue.empty():
                    items = output_queue.get()
                    for itm in items['Item']:
                        itm['ebay_sites'] = ','.join(items_dict[itm['ItemID']])
                        itm['lnkr_query_id'] = q_id
                        items_results.append(EbayItem(**itm))
                    output_queue.task_done()
                EbayItem.objects.insert(items_results)
                del items_results


    def get_seller_details(self, seller_id=None, out_q=None, err_q=None):
        
        url = "http://open.api.ebay.com/shopping"
        
        payload = { 'callname' : 'GetUserProfile',
                    'responseencoding' : 'JSON',
                    'appid' : self.api_key,
                    'version' : '967',
                    'IncludeSelector' : 'FeedbackHistory',
                    'UserID' : seller_id
                    }
        
        r = requests.get(url, params=payload)
        j_seller = json.loads(r.text)
        j_slr = j_seller['User']
        # include stats about feedbacks received
        j_slr['UniqueNegativeFeedbackCount'] = ''
        j_slr['UniqueNeutralFeedbackCount'] = ''
        j_slr['UniquePositiveFeedbackCount'] = ''
        for k in j_seller['FeedbackHistory'].keys():
            if k[:6] == "Unique":
                j_slr[k] = j_seller['FeedbackHistory'][k]
                
        if j_seller['Ack'] == 'Success':
            out_q.put(j_slr)
        else:
            ERR_MSG = {'platform' : 'ebay',
                       'api_call' : 'GetUserProfile',
                       'input' : 'seller_id: {}'.format(seller_id),
                       'error_message' :  j_seller['Errors']['ShortMessage']}
            err_q.put(ERR_MSG)
        
        
    def get_multiple_sellers(self, seller_list=[], max_threads=20):
        output_queue = Queue()
        error_queue = Queue()
        seller_matrix = [ seller_list[i:i+max_threads] for i in range(0, len(seller_list), max_threads) ]
        for batch in seller_matrix:
            thread_list = []
            for seller_id in batch:
                thread_call = Thread(target=self.get_seller_details, kwargs={'seller_id' : seller_id,
                                                                             'out_q' : output_queue,
                                                                             'err_q' : error_queue})
                thread_list.append(thread_call)
                thread_call.start()
            for t in thread_list:
                t.join()
        
        seller_results = []
        while not output_queue.empty():
            seller = output_queue.get()
            seller_results.append(seller)
            output_queue.task_done()
        
        error_list = []
        while not error_queue.empty():
            error_list.append(error_queue.get()) 
        
        return seller_results, error_list
    
