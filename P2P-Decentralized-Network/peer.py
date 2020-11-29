from client import Client
from server import Server
from tracker import Tracker
from config import Config
#from downloader import downloader
from torrent import *  # assumes that your Torrent file is in this folder
from threading import Thread
import uuid

"""
class Peer():
    
    SEEDER = 2;
    LECHES = 1;
    PEER = 0;

    # copy and paste here your code implementation from the peer.py in your Labs
    
    def __init__(self):
        self.role = PEER # default role
        pass

    """




class Peer:
    """
    In this part of the peer class we implement methods to connect to multiple peers.
    Once the connection is created downloading data is done in similar way as in TCP assigment.
    """
    SERVER_PORT = 5000
    CLIENT_MIN_PORT_RANGE = 5001


    MAX_NUM_CONNECTIONS = 10
    MAX_UPLOAD_RATE = 100
    MAX_DOWNLOAD_RATE = 1000

    PEER = 'peer'
    LEECHER = 'leecher'
    SEEDER = 'seeder'

    #def __init__(self, role=PEER, server_ip_address='172.20.176.1'): DIFFERENT computer
    def __init__(self, role=SEEDER, server_ip_address='10.0.0.246'):#Run client role = PEER or LEECHER, Don't run client role = SEEDER

  #  def __init__(self, role=SEEDER, server_ip_address='10.0.0.246'):#Run client role = PEER or LEECHER, Don't run client role = SEEDER

        """
        Class constructor
        :param server_ip_address: used when need to use the ip assigned by LAN
        """
        
        #self.client = Client('127.0.0.4', 5000)
        self.server_ip_address = server_ip_address
        self.id = uuid.uuid4()  # creates unique id for the peer
        self.role = role
        self.torrent = Torrent("age.torrent")
        self.server = Server(self.torrent, self.id, server_ip_address, self.SERVER_PORT)  # inherits methods from the server
        self.tracker = None
        self.swarm = [('127.0.0.1', 5000), ('127.0.0.2', 5000)] #Test
        

    def run_server(self):
        """
        Starts a threaded server
        :return: VOID
        """
        try:
            # must thread the server, otherwise it will block the main thread
            Thread(target=self.server.run, daemon=False).start()
            print("Server started.........")
        except Exception as error:
            print(error)  # server failed to run

    """def run_client(self, announce=False):
        try:
            Thread(target=self.client.run, daemon=False).start()
            print("Client started.........")

            
        except Exception as error:
            print(error)  # server failed to run"""


    def run_tracker(self, announce=False):
        """
        Starts a threaded tracker
        :param announce: True if this is the first announce in this network
        :return: VOID
        """
        try:
            
            #if self.server:
                
                #self.tracker = Tracker(self.server, self.torrent, announce)
                #Thread(target=self.tracker.run, daemon=False).start()
                #print("Tracker running.....")

            if self.role != 'seeder': #Seeder does not need client to download

                self.client = Client(self.torrent, announce, self.tracker, str(self.id),  self.server_ip_address, 5001)
                Thread(target=self.client.run, daemon=False).start()
                print("Client started.........")
                
                
                
        except Exception as error:
            print(error)  # server failed to run


# runs when executing python3 peer.py
# main execution
if __name__ == '__main__':
    # testing
    #peer = Peer(role='peer')
    peer = Peer()
    print("Peer: " + str(peer.id) + " started....")
    peer.run_server()
    #print("test")
    peer.run_tracker()
    #peer.run_client()


    

