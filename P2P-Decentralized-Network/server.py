""" Add your Server class from your TCP assignment here """
########################################################################################################################
# Class: Computer Networks
# Date: 02/03/2020
# Lab3: TCP Server Socket
# Goal: Learning Networking in Python with TCP sockets
# Student Name: John To 
# Student ID: 917507752
# Student Github Username: l90320825
# Lab Instructions: No partial credit will be given in this lab
# Program Running instructions: python3 server.py # compatible with python version 3
#
########################################################################################################################

# don't modify this imports.
import socket
import pickle
#from client_handler import ClientHandler
from threading import Thread
from uploader import Uploader
from torrent import Torrent


MAX_NUM_CONN = 10



class Server(object):
    """
    The server class implements a server socket that can handle multiple client connections.
    It is really important to handle any exceptions that may occur because other clients
    are using the server too, and they may be unaware of the exceptions occurring. So, the
    server must not be stopped when a exception occurs. A proper message needs to be show in the
    server console.
    """
    MAX_NUM_CONN = 10 # keeps 10 clients in queue

    def __init__(self, torrent, peer_id, host="127.0.0.1", port = 12000):
        """
        Class constructor
        :param host: by default localhost. Note that '0.0.0.0' takes LAN ip address.
        :param port: by default 12000
        """
        self.host = host
        self.port = port
        self.torrent = torrent
        self.peer_id = peer_id
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TODO: create the server socket
        self.client_handlers = {}  # initializes client_handlers list
       # self.serversocket.bind((self.host, self.port))
        self.serversocket.bind((self.host, self.port))

    def _listen(self):
        """
        # TODO: puts the server in listening mode.
        # TODO: if succesful, print the message "Server listening at ip/port"
        :return: VOID
        """
        try:
           
            self.serversocket.listen(MAX_NUM_CONN)

            print(socket.gethostbyname(socket.gethostname()))
            
            print("Listening at " + self.host + "/" + str(self.port))
            
            # your code here
        except:
            print("Something wrong")
            self.serversocket.close()

    def threaded_client(self, clienthandler, addr):
        """
        #TODO: receive, process, send response to the client using this handler.
        :param clienthandler:
        :return:
        """

        client_id = addr[1]
        print(addr[1])
        self.send(clienthandler, "Server recived")
        self.client_handlers[client_id] = clienthandler
        # Create Client Handler?
        data = self.receive(clienthandler)

        print(data)

        data = self.receive(clienthandler)

        print(data)

        

        upload = Uploader(self.peer_id, self, clienthandler, None, self.torrent)

        #Thread(target=upload.run, daemon=False).start()

        upload.run()


        # P2P Server stuff
        while True:
            data = self.receive(clienthandler)
            if not data:
                print("Bad Input")
                break
            print(data)
            # Do Stuff with Data
        clienthandler.close()


        #self.receive(clienthandler)
        #client_handler = ClientHandler(self, clienthandler, addr)
        #client_handler.run()
        #self.client_handlers[client_id] = client_handler
        #print(self.client_handlers)
        #print("self.receive(clienthandler)")
             # creates a stream of bytes
        #self.send(clienthandler, "server got the data")
            


    


    def _accept_clients(self):
        """
        #TODO: Handle client connections to the server
        :return: VOID
        """
        while True:
            try:
               clienthandler, addr = self.serversocket.accept()
               client_id = {'clientid': addr[1]}
               self._send_clientid(clienthandler, client_id)
               print("Server recev")
               print(addr)
               Thread(target=self.threaded_client, args=(clienthandler, addr)).start() 

            except Exception as e:
                print(e)
                self.send(clienthandler, "Something wrong about the server")
                self.serversocket.close()
               # handle exceptions here

              

    def _send_clientid(self, clienthandler, clientid):
        """
        # TODO: send the client id to a client that just connected to the server.
        :param clienthandler:
        :param clientid:
        :return: VOID
        """
        data = {'clientid': clientid}
        self.send(clienthandler, data)
          


    def send(self, clienthandler, data):
        """
        # TODO: Serialize the data with pickle.
        # TODO: call the send method from the clienthandler to send data
        :param clienthandler: the clienthandler created when connection was accepted
        :param data: raw data (not serialized yet)
        :return: VOID
        """
        
        serialized_data = pickle.dumps(data) # serialized data
        clienthandler.send(serialized_data)
       

    def receive(self, clientsocket, MAX_BUFFER_SIZE=4096):
        """
        TODO: Deserializes the data with pickle
        :param clientsocket:
        :param MAX_BUFFER_SIZE:
        :return: the deserialized data
        """
        # while True:
        #     raw_data = clientsocket.recv(MAX_BUFFER_SIZE)
        #     if not raw_data:
        #         break
        #     data = pickle.loads(raw_data)
        #     print(data)
        #     return data
        #
        # return pickle.loads(raw_data)

        raw_data = clientsocket.recv(MAX_BUFFER_SIZE)
        data = pickle.loads(raw_data)
        return data


    def run(self):
        """
        Already implemented for you
        Run the server.
        :return: VOID
        """
        self._listen()
        print("Server running")
        self._accept_clients()




