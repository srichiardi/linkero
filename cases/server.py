import socket
import sys
import time
import json

def main():
    HOST = 'localhost'
    PORT = 50010

    # creating the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # binding the socket to host and port
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print('Bind failed. Error Code: ' + str(msg[0]) + \
              '\n\tMessage: ' + msg[1])
        time.sleep(3)
        sys.exit()

    # start lisening on socket
    s.listen()

    while True:
        # wait to accept a connection - blocking call
        client, addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))

        chunks = []
        i = 0
        while True:
            chunk = client.recv(256).decode('utf-8')
            i =+ 1
            print('chunk {} len {}'.format(i, len(chunk)))
            if chunk[-16:] == '_QUERY_COMPLETED':
                chunks.append(chunk[:-16])
                break
            chunks.append(chunk)
        request = ''.join(chunks)

        req_json = json.loads(request)

        print("query received")
        print('user: {}, platform: {}'.format(req_json['user'], req_json['query_platform']))
        reply_json = {'ack' : 'query_submitted'}
        request = json.dumps(reply_json)
        request += '_REQ_COMPLETED'
        client.sendall(request.encode('utf-8'))
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        time.sleep(3)
        print("shutting down in 3 sec")
        time.sleep(3)
        sys.exit()


if __name__ == "__main__":
    main()