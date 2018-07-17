import requests
import json
from threading import Thread
from queue import Queue
from urllib.parse import urlencode
from collections import defaultdict
from cases.ebaySettings import globalSiteMap


class EbayApi():
    def __init__(self):
        self.api_key = 'StefanoR-ebayFric-PRD-19f17700d-ff298548'
        
        
    def find_items_multi_sites(self, e_sites=['US'], kwd=None, s_id=None, s_desc=None):
        """ Start up to 20 parallel threads, one each site id """
        threads_list = []
        out_queue = Queue()
        for site in e_sites:
            thread_call = Thread(target = self.find_items_multi_pages,
                                 kwargs = {'out_q' : out_queue,
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
        while out_queue.not_empty():
            batch = out_queue.get()
            for item, i_dict in batch.items():
                site = i_dict['ebaySite']
                seller = i_dict['sellerUserName']
                if site not in items_dict[item]:
                    items_dict[item].append(site)
                if seller not in seller_list:
                    seller_list.append(seller)
                
            out_queue.task_done()
            
        return items_dict, seller_list            
    
        
    def find_items_multi_pages(self, out_q=None, e_site='US', kwd=None, s_id=None, s_desc=None):
        """ pull results of advanced search and return dictionary with items id for keys and seller id,
        site id as values """
        tot_pages = 1
        page = 1
        items_dict = defaultdict(dict)
        while page <= min(100, tot_pages):
            result_set = find_items(ebay_site = e_site, page_nr = page, keywords = kwd, seller_id = s_id,
                                    search_desc = s_desc)
            tot_pages = int(result_set['findItemsAdvancedResponse'][0]['paginationOutput'][0]['totalPages'][0])
            page += 1
            
            for item in result_set['findItemsAdvancedResponse'][0]['searchResult'][0]['item']:
                items_dict[item['itemId'][0]]['sellerUserName'] = item['sellerInfo'][0]['sellerUserName'][0]
                items_dict[item['itemId'][0]]['ebaySite'] = ebay_site
        
        if out_q:
            out_q.put(items_dict)
        else:
            return items_dict
            


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
        
        return json.loads(r.text)
        

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
        
        
    def get_multi_items_threaded(self, items_dict={}, max_threads=20):
        
        # generating a dict sites with lists of items
        sites_priority = ('GB', 'US', 'IE', 'CA-EN', 'AU', 'IT', 'FR', 'CA-FR', 'ES', 'AT', 'BE-FR', 'DE', 'MOTOR', 'BE-NL', 'NL', 'CH', 'HK', 'IN', 'MY', 'PH', 'PL', 'SG')
        items_by_sites = defaultdict(list)
        for item_id, e_sites in items_dict.items():
            for p_site in sites_priority:
                if p_site in e_sites:
                    items_by_sites[p_site].append(item)
                    break
        
        output_queue = Queue()
        for site, items in items_by_sites.items():
            items_strings = [ ','.join(items[i:i+20]) for i in xrange(0, len(items), 20) ]
            threads_list = []
            # batches of 20 strings of 20 items  
            items_matrix = [ items_strings[i:i+max_threads] for i in xrange(0, len(items_strings), max_threads) ]
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
        while output_queue.not_empty():
            items = output_queue.get()
            for itm in items['Item']:
                itm['ebay_sites'] = ','.join(items_dict[itm['ItemID']])
                items_results.append(itm)
            output_queue.task_done()
        
        return items_results        


    def get_seller_details(self, out_q=None, seller_id):
        
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
        if out_q:
            out_q.put(json.loads(r.text))
        else:
            return json.loads(r.text)
        
        
    def get_multiple_sellers(self, seller_list=[], max_threads=20):
        output_queue = Queue()
        seller_matrix = [ seller_list[i:i+max_threads] for i in xrange(0, len(seller_list), max_threads) ]
        for batch in seller_matrix:
            thread_list = []
            for seller_id in batch:
                thread_call = Thread(target=self.get_seller_details, kwargs={'seller_id' : seller_id,
                                                                             'out_q' : output_queue})
                thread_list.append(thread_call)
                thread_call.start()
            for t in thread_list:
                t.join()
        
        seller_results = []
        while output_queue.not_empty():
            seller = output_queue.get()
            seller_results.append(seller)
            output_queue.task_done()
        
        return seller_results
    