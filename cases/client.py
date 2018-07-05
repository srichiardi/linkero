import sys
import socket
import json



def main():
    
    
    query = """SELECT cld.ITEM_ID

FROM PRS_SECURE_V.DW_LSTG_ITEM_COLD cld
INNER JOIN ACCESS_VIEWS.DW_USERS usr
ON (cld.SLR_ID = usr.USER_ID)

WHERE usr.USER_SLCTD_ID = """

    # connect to server
    HOST = 'localhost'
    PORT = 50010
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.connect((HOST,PORT))

    # send data query
    query += "QUERY_COMPLETED"
    s.send(query)

    results = ''
    # receiving the results
    while True:
        results += s.recv(1024)
        if results[-15:] == 'REPLY_COMPLETED':
            break

    resultsList = json.loads(results[:-15])



