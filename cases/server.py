import socket
import sys
import pyodbc
import Queue
import threading
import json
import time



## Query Deamon Thread
class ThreadQueryDaemon(threading.Thread):
    """ Thread DAEMON to execute in sequence data requests """
    def __init__(self, connection, conn, queryQueue):
        threading.Thread.__init__(self)
        self.connection = connection
        self.conn = conn
        self.queryQueue = queryQueue

    def run(self):
        while True:
            client = self.queryQueue.get()
            clientthread(self.connection, self.conn, client)
            self.queryQueue.task_done()


# Function for handling connections. This will be used to create threads
def clientthread(connection, conn, client):
    """ function to manage data fetching and connection restore """
     
    # pull the string with query from the client
    query = ''
    while True:
        # receiving from client
        query += client.recv(1024)
        if query[-15:] == 'QUERY_COMPLETED':
            break
    print "query received"
    
    # try to reconnect if connection is lost
    try:
        cursor = conn.cursor()
    except pyodbc.ProgrammingError as e:
        try:
            conn = connectToDb(connection)
        except Exception as e:
            print "Reconnect attempt failed.\n\
Shut down and restart to use the trasforms."
            time.sleep(3)
            sys.exit()
        else:
            cursor = conn.cursor()
            print "Connection restored."

    print "connection to DB confirmed"
    
    # Execute the SQL query
    cursor.execute(query[:-15])

    # create list with headers
    columns = [col[0] for col in cursor.description]

    # parse results in json string format
    results = []
    for row in cursor.fetchall():
        records = map(str, row)
        results.append(dict(zip(columns, records)))

    print "Found %d records" % len(results)
    
    # reply to the client
    reply = json.dumps(results)
    reply += 'REPLY_COMPLETED'
    client.sendall(reply)

    # closing the connection
    client.shutdown(socket.SHUT_RDWR)
    client.close()


def dbConnection():
    user, pw = ('pippo', 'baudo')
    driver = 'Teradata'
    server = 'mozart.vip.ebay.com'
    connection = 'DRIVER={%s};DBCNAME=%s;UID=%s;PWD=%s' % (driver, server, user, pw)
    return connection


def connectToDb(connection):
    try:
        print "Connecting to Teradata, please wait..."
        conn = pyodbc.connect(connection)
    except pyodbc.Error as e:
        raise Exception('Teradata Login Failed!')
    else:
        print 'Teradata connection established.'
        return conn


def main():
    HOST = 'localhost'
    PORT = 50010

    # creating the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # binding the socket to host and port
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print 'Bind failed. Error Code: ' + str(msg[0]) + \
              '\n\tMessage: ' + msg[1]
        time.sleep(3)
        sys.exit()

    # connecting for first time
    while True:
        connection = dbConnection()
        try:
            conn = connectToDb(connection)
        except Exception as e:
            print str(e)
            toDo = raw_input("Invalid login. Retry? (Yes/No): ")
            if toDo.strip()[0].lower() == "y":
                continue
            else:
                print "Shutting down the transform server."
                time.sleep(3)
                sys.exit()
        else:
            # exit loop
            break

    # start lisening on socket
    s.listen(10)

    # create Queue and start query process thread
    queryQueue = Queue.Queue()

    # start the Qeury Deamon and pass the cursor
    queryDaemon = ThreadQueryDaemon(connection, conn, queryQueue)
    queryDaemon.setDaemon(True)
    queryDaemon.start()

    print 'Ready to execute transforms.'

    # now keep talking with the client
    while True:
        # wait to accept a connection - blocking call
        client, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])

        # queue client requests and process sequentially
        queryQueue.put(client)