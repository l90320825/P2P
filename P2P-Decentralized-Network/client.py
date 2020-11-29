""" Add your Client class from your TCP assignment here """

# copy and paste your code from your client.py file
########################################################################################################################
# Class: Computer Networks
# Date: 02/03/2020
# Lab3: TCP Client Socket
# Goal: Learning Networking in Python with TCP sockets
# Student Name:
# Student ID:
# Student Github Username:
# Instructions: Read each problem carefully, and implement them correctly.  No partial credit will be given.
########################################################################################################################


from torrent import Torrent
from message import Message
from file_manager import FileManager
from downloader import Downloader
import socket
import pickle




######################################## Client Socket ###############################################################3
"""
Client class that provides functionality to create a client socket is provided. Implement all the TODO parts 
"""

class Client(object):

    def __init__(self, message, torrent, announce, tracker, peerid, host="127.0.0.1", port = 12000):
        """
        Class constructor
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        self.tracker = tracker
        self.client_id = None
        self.announce = announce
        self.torrent = torrent
        self.peerid = peerid
        self.message = message #Send message
        self.file_manager = FileManager(torrent, peerid)



    def connect(self, server_ip_address, server_port):
        """
        TODO: Create a connection from client to server
        :param server_ip_address:
        :param server_port:
        :return:
        """
        #TODO: 1. use the self.client to create a connection with the server
       
        self.client.connect((server_ip_address, server_port))
         

        #TODO: 2. once the client creates a successful connection, the server will send the client id to this client.
        #      call the method set_client_id() to implement that functionality.

        self.set_client_id()

        # data dictionary already created for you. Don't modify.
        #data = {'student_name': self.student_name, 'github_username': self.github_username, 'sid': self.sid}
        print("Handshaking")
        data = self.message.handshake
        data['info_hash'] = self.torrent.info_hash()
        data['peer_id'] = self.peerid
        #print(data)

        

        self.send(data)

        data = self.receive()

        print(data)

        data = self.message.interested #Tell server client is interested to download

        self.send(data)


        download = Downloader(self.client, self.peerid, self.torrent, 1, 1, self)

        download.run()

        """
        pieceIndex = 0
        while pieceIndex < 5:

            for i in range(8): # Download first piece
                data = self.message.request
                data['index'] = pieceIndex
                data['begin'] = self.torrent.block_size() * i
                data['length'] = self.torrent.block_size()

                self.send(data)
                data = self.receive()
                #print(data)
            
                blockIndex = self.file_manager.block_index(data['begin'])
                self.file_manager.flush_block(data['index'],  blockIndex, data['block'])
                self.message._bitfield['bitfield'][pieceIndex][blockIndex] = True

            pieceIndex += 1

            """
           




        

        

        

        




        while True: # client is put in listening mode to retrieve data from server.
            data = self.receive()
            if not data:
                break
            print(data)
            #data = self.message.interested

            # do something with the data
        self.close()

    def send(self, data):
        """
        Serializes and then sends data to server
        :param data:
        :return:
        """
        serialized_data = pickle.dumps(data) # serialized data
        self.client.send(serialized_data)

    def receive(self, MAX_BUFFER_SIZE=4090):
        """
        Desearializes the data received by the server
        :param MAX_BUFFER_SIZE: Max allowed allocated memory for this data
        :return: the deserialized data.
        """
        
        raw_data = self.client.recv(MAX_BUFFER_SIZE) # deserializes the data from server
        return pickle.loads(raw_data)

    def set_client_id(self):
        """
        Sets the client id assigned by the server to this client after a succesfull connection
        :return:
        """
        data = self.receive() # deserialized data
        client_id = data['clientid'] # extracts client id from data
        self.client_id = client_id # sets the client id to this client
        print("Client id " + str(self.client_id) + " assigned by server")

    def close(self):
        """
        TODO: close this client
        :return: VOID
        """
        self.client.close()

    def run(self):

        self.client.bind(("", self.port)) #connect to different pc, change to 127.0.0.1 if localhost
        self.connect("10.0.0.246", 5000)#Test

      #  self.client.bind(("", self.port))
    #    self.connect("172.20.176.1", 5000)


"""
    def _bind(self):
        
        # TODO: bind host and port to this server socket
        :return: VOID
        

        self.serversocket.bind((self.host, self.port))
        #self.serversocket.listen(10)
        while True:
            message, clientAddress = self.serversocket.recvfrom(2048)
            print("Client recieve")
            print(clientAddress)
            message = pickle.loads(message)
            print(message)
            entry = {'nodeID': message['nodeId'], 'ip_address': message['ip'], 'port': message['port'], 'info_hash': message['info_hash'], 'last_changed': 'timestamp' }
            print(entry)
            self.tracker._routing_table_add(message['info_hash'], entry)
            self.connect(message['ip'], 5000)

            """



    

# main execution
if __name__ == '__main__':
    server_ip_address = "127.0.0.1"  # don't modify for this lab only
    server_port = 12000 # don't modify for this lab only
    #client = Client(False)
    #client.connect(server_ip_address, server_port)

# How do I know if this works?
# when this client connects, the server will assign you a client id that will be printed in the client console
# Your server must print in console all your info sent by this client
# See README file for more details

