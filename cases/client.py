import sys
import socket
from subprocess import Popen
import time
import json


def myclient():

    # connect to server
    HOST = 'localhost'
    PORT = 50010
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.connect((HOST,PORT))
    
    query_json = { 'user' : 'stefano',
                  'query_platform' : 'ebay',
                  'query_type' : 'listings',
                  'query_id' : 123,
                  'query_kwargs' : { 'ebay_sites' : ['US', 'DE', 'GB'],
                                     'search_desc' : False,
                                     'seller_id' : 'someseller',
                                     'keyword' : 'somekeyword'
                                     },
                  'delivery_email' : 'ellinkero@yahoo.com'
                  }
    
    query = json.dumps(query_json)

    # send data query
    query += "_QUERY_COMPLETED"
    s.send(query.encode('utf-8'))

    results = []
    # receiving the results
    while True:
        reply = s.recv(256).decode('utf-8')
        if reply[-14:] == '_REQ_COMPLETED':
            results.append(reply[:-14])
            break
        results.append(reply)       

    response = ''.join(results)
    print("query len: {}".format(len(query)))
    print("reply len: {}".format(len(response)))
    print(results)


def callserver():
    print("calling server")
    process = Popen(['C:/Users/srichiardi/AppData/Local/Programs/Python/Python35/python.exe','C:/Users/srichiardi/Desktop/linkero/servertest.py'])
    time.sleep(1)
    print("server called")
    time.sleep(1)
    print("exiting...")
    time.sleep(2)
    print("...now!")
    sys.exit()
