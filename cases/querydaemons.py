import socket
import json
import time
from queue import Queue
from threading import Thread, Event
from pymongo import MongoClient
from ebayapi import EbayApi


## server loop
def main():
    ''' receives and queues data requests INPUT: routine kwargs + query id + platform id + report type + user id '''
    HOST = 'localhost'
    PORT = 50010
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print 'Bind failed. Error Code: ' + str(msg[0]) + \
              '\n\tMessage: ' + msg[1]
        time.sleep(3)
        sys.exit()
    
    # connect to MongoDB
    DB_HOST = 'attila'
    DB_PORT = 27018
    DB_USER = 'linkero-user'
    DB_PSWD = '123linkero123'
    connect_url = 'mongodb://{};{}@{}:{}'.format(DB_USER, DB_PSWD, DB_HOST, DB_PORT)
    client = MongoClient(connect_url)
    linkero_db = client['linkero-db']
    
    # start request coordinator daemon
    query_queue = Queue()
    stop_event = Event()
    req_coord = RequestCoordinator(query_queue, stop_event, linkero_db)
    req_coord.start()
    
    # listen to client connections
    s.listen()
    while True:
        client, addr = s.accept()
        # receive query and save it to queue
        while True:
            query += client.recv(1024).decode('utf-8')
            if query[-16:] == '_QUERY_COMPLETED':
                break
            
        # close connection with client
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        query_queue.put(query[:-16])
    
    # shut everything down if more than 5 min passed since last report completed
    stop_event.set()


## report daemon
''' executes sequentially all data requests in the queue '''
class RequestCoordinator(Thread):
    def __init__(self, in_queue, stop_event, mongo_db):
        super().__init__()
        self.in_queue = in_queue
        self.route_dict = { 'ebay' : { 'listings' : ebay_listing_report } }
        self.daemon = True
        self.stop_event = stop_event
        self.mongo_db = mongo_db
        
    def run(self):
        while not self.stop_event.is_set():
            query = json.loads(self.in_queue.get())
            self.in_queue.task_done()
            # unpack query
            j_query = json.loads(query)
            # generate file with report
            report_attachment = self.route_dict[j_query['query_platform']][j_query['report_type']](j_query['query_kwargs'])
            # send email

# retrieve query from queue, check the report type and start the relative routine


## ebay listing process
''' retieves ebay listings data based on seller_id and/or keywords '''
def ebay_listing_report(mongo_db):
    lstg_dtls_collection = mongo_db['getMultipleItems']
    ea = EbayApi()
    items = ea.get_multiple_items()
    for item in items:
        lstg_dtls_collection.save(item)


# find items advanced

# get items details

# get seller details


## query threads
''' get data from API and save it in mongo '''