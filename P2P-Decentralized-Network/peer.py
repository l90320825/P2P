from client import Client
from server import Server
from tracker import Tracker
from config import Config
# from downloader import downloader
from torrent import *  # assumes that your Torrent file is in this folder
from threading import Thread
import uuid
from message import Message
import socket
from file_manager import FileManager
import time
from htpbs import ProgressBars

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
    SERVER_IP = '127.0.0.2'
    NUM_SERVER = 2
    SERVER_PORT = 5000
    CLIENT_MIN_PORT_RANGE = 5001

    MAX_NUM_CONNECTIONS = 10
    MAX_UPLOAD_RATE = 100
    MAX_DOWNLOAD_RATE = 1000

    PEER = 'peer'
    LEECHER = 'leecher'
    SEEDER = 'seeder'

    #def __init__(self, role=PEER, server_ip_address='172.20.176.1'): DIFFERENT computer
    #def __init__(self, role=SEEDER, server_ip_address='10.0.0.246'):#Run client role = PEER or LEECHER, Don't run client role = SEEDER
    
    #def __init__(self, role=PEER, server_ip_address=socket.gethostbyname(socket.gethostname())):
    def __init__(self, role=PEER, server_ip_address=SERVER_IP):#Run client role = PEER or LEECHER, Don't run client role = SEEDER

        """
        Class constructor
        :param server_ip_address: used when need to use the ip assigned by LAN
        """

        # self.client = Client('127.0.0.4', 5000)
        self.server_ip_address = server_ip_address
        self.id = uuid.uuid4()  # creates unique id for the peer
        self.role = role
        self.torrent = Torrent("age.torrent")
        self.server = Server(self.torrent, self.id, server_ip_address,
                             self.SERVER_PORT)  # inherits methods from the server
        self.client = None
        self.tracker = None  # Tracker(self.server, self.torrent, False) #bool - announce?
        self.swarm = []  # [('127.0.0.1', 5000), ('127.0.0.2', 5000), ('127.0.0.3', 5000)]  # Test
        self.message = Message()  # Initialize bitfield for this peer
        self.file_manager = FileManager(self.torrent, self.id)
        self.progressbars = ProgressBars(num_bars=self.NUM_SERVER)

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

    """
    def run_client(self, announce=False):
        try:
            Thread(target=self.client.run, daemon=False).start()
            print("Client started.........")

            
        except Exception as error:
            print(error)  # server failed to run
    """

    def run_tracker(self, announce=False):
        """
        Starts a threaded tracker
        :param announce: True if this is the first announce in this network
        :return: VOID
        """
        try:
            if self.server:
                if self.role == 'peer':
                    announce = True
                self.tracker = Tracker(self, self.server, self.torrent, announce)
                t1 = Thread(target=self.tracker.run, daemon=False)
                t1.start()
                print("Tracker running.....")

                info_hash = self.torrent.info_hash()

                t1.join()

               




                
            if self.role != 'seeder':  # Seeder does not need client to download
                
               # while len(self.swarm) < 1:
                    
                    #print("Tracker DHT: ", self.tracker.get_DHT(info_hash), "Look here")
                
                print("Searching seeder")
                time.sleep(5)


                while len(self.swarm) < 1:
                    print("Searching seeder")
                    time.sleep(10)




                self.message.init_bitfield(self.torrent.num_pieces())  # Initialize this bitfield
                self.file_manager.create_tmp_file()

                try:
                    size = len(self.swarm[info_hash])

                except:
                    size = len(self.swarm)
                print("size", size)
                self.progressbars = ProgressBars(num_bars=size)

                i = 0

                # Peer needs to get the DHT from tracker at the right time so that
                # the tracker is updated before starting the downloads
                # Perhaps this could be threaded or put in some while loop? Lemme know what you think. - Chun
                self.swarm = self.tracker.get_DHT(self.torrent.info_hash())
                print("Swarm: ", self.swarm)

               # print(self.swarm[1][0])
                port = self.CLIENT_MIN_PORT_RANGE
               
                for i in range(size):
                    peer_ip = self.swarm[i][0]
                    self._connect_to_peer(i , port, peer_ip)
                    port += 1
               






                







                """
                self.client = Client(self, 0, self.message, self.torrent, announce, self.tracker, str(self.id), self.TARGET_IP,
                                     self.server_ip_address, 5001)
                Thread(target=self.client.run, daemon=False).start()

                time.sleep(1)

                
                
                self.client2 = Client(self, 1, self.message, self.torrent, announce, self.tracker, str(self.id), self.TARGET2_IP,
                                     self.server_ip_address, 5002)
                Thread(target=self.client2.run, daemon=False).start()

                time.sleep(1)

                
                
                self.client3 = Client(self, 2, self.message, self.torrent, announce, self.tracker, str(self.id), self.TARGET3_IP,
                                     self.server_ip_address, 5003)
                Thread(target=self.client3.run, daemon=False).start()
                
                """
               
                
               # print("Client started.........")

            # Get an array of (ip, port) that are connected to the torrent file
            #self.swarm = self.tracker.get_DHT()

        except Exception as error:
            print(error)  # Tracker or Client error


    def _connect_to_peer(self, threadID, client_port_to_bind, peer_ip_address):
        """
        TODO: * Create a new client object and bind the port given as a
              parameter to that specific client. Then use this client
              to connect to the peer (server) listening in the ip
              address provided as a parameter
              * Thread the client
              * Run the downloader
        :param client_port_to_bind: the port to bind to a specific client
        :param peer_ip_address: the peer ip address that
                                the client needs to connect to
        :return: VOID
        """
        try:
           # print("threadId", threadID)
            self.client = Client(self, threadID, self.message, self.torrent, 1, self.tracker, str(self.id), peer_ip_address,
                                     self.server_ip_address, client_port_to_bind)
            Thread(target=self.client.run, daemon=False).start()
            print("Client started.........")
                            
        except Exception as error:
            print(error)  # server failed to run        


# runs when executing python3 peer.py
# main execution
if __name__ == '__main__':
    # testing
    # peer = Peer(role='peer')
    peer = Peer()
    #print(peer.torrent.info_hash())
    print("\n***** P2P client App *****\n")
    print("Peer: " + str(peer.id) + " started....")
    print("Max download rate: 2048 b/s")
    print("Max upload rate: 2048 b/s\n")
    print("Torrent: " + peer.torrent.torrent_path)
    print("file: "+ peer.torrent.file_name())
    print("seeder/s: " + str(peer.server_ip_address) + ":" + str(peer.SERVER_PORT))
    peer.run_server()
    peer.run_tracker()
    # peer.run_client()
