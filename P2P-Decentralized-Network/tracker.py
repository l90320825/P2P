from server import Server
from torrent import Torrent
import socket
import pickle
import threading
import bencodepy
import uuid
import hashlib




class Tracker:

    DHT_PORT = 12001
    DHT_IP = "127.0.0.1"


    def __init__(self, server, torrent, announce=False):
        self.server = server
        self.torrent = torrent
        self.torrent_info_hash = torrent.info_hash()
        self.announce = announce
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.bind((self.DHT_IP, self.DHT_PORT))
        self.non_broadcast_socket = None
        self.query_ip = None
        self.query_port = None
        self.action = None
        self.nodeID = None
        self.token = None
        self.id = uuid.uuid4()

        # will story a list of dictionaries representing entries in the routing table
        # dictionaries stored here are in the following form
        # {'nodeID': '<the node id is a SHA1 hash of the ip_address and port of the server node and a random uuid>',
        #  'ip_address': '<the ip address of the node>', 'port': '<the port number of the node',
        #  'info_hash': '<the info hash from the torrent file>', last_changed': 'timestamp'}
        self._routing_table = {}

    def _get_torrent_info_hash(self):
        """
        TODO: creates the torrent info hash (SHA1) from the info section in the torrent file
        :return:
        """
        

        return self.torrent_info_hash  # returns the info hash

    def add_peer_to_swarm(self, peer_id, peer_ip, peer_port):
        """
        TODO: when a peers connects to the network adds this peer
              to the list of peers connected
        :param peer_id:
        :param peer_ip:
        :param peer_port:
        :return:
        """
        pass  # your code here

    def remove_peer_from_swarm(self, peer_id):
        """
        TODO: removes a peer from the swarm when it disconnects from the network
              Note: this method needs to handle exceptions when the peer disconnected abruptly without
              notifying the network (i.e internet connection dropped...)
        :param peer_id:
        :return:
        """
        pass  # your code here

    def encode(self, message):
        """
        bencodes a message
        :param message: a dictionary representing the message
        :return: the bencoded message
        """
        return bencodepy.encode(message)


    def decode(self, bencoded_message):
        """
        Decodes a bencoded message
        :param bencoded_message: the bencoded message
        :return: the original message
        """
        return bencodepy.decode(bencoded_message)

    def broadcast(self, message, self_broadcast_enabled=False):
        """
        TODO: broadcast the list of connected peers to all the peers in the network.
        :return:
        """
        try:
            #print(message)
            encoded_message = self.encode(message)
            print("bencoded = " + encoded_message.decode(('utf8')) + "\n")
            self.udp_socket.sendto(encoded_message, ('<broadcast>', self.DHT_PORT))
            print("Message broadcast.....")
        except socket.error as error:
            print(error)


    def send_udp_message(self, message, ip, port):
        try:
            #new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = self.encode(message)
            print("bencoded = " + message.decode(('utf8')) + "\n")
            #new_socket.sendto(message, (ip, port))
            self.udp_socket.sendto(message, (ip, port))
        except:
            print("error")

    def broadcast_listerner(self):
        try:
            print("Listening at DHT port: ", self.DHT_PORT)
            while True:
                raw_data, sender_ip_and_port = self.udp_socket.recvfrom(4096)
                #print(self.DHT_IP !=  sender_ip_and_port[0])
                if raw_data and self.DHT_IP !=  sender_ip_and_port[0]:
                    data = self.decode(raw_data)
                    #pickle.loads(data)
                   
                   # data = dict(data)
                   # print(data[b't'].decode(('utf8')))
                   # for key, item in data.items(): 
                      #  print(key.decode(('utf8')))



                    #print(data)

                    #self.process_query(data)
                    ip_sender = sender_ip_and_port[0]
                    port_sender = sender_ip_and_port[1]
                    self.query_ip = ip_sender
                    self.query_port =  port_sender 

                    if data[b'y'].decode(('utf8')) == "r":
                        self.process_query(data)
                    else:
                        self.send_response(data)

                    #print("Data received by sender", data, ip_sender, port_sender)
                    #node = (ip_sender, port_sender)
                    #self._routing_table_add(node)


                    

        except:
            print("Error listening at DHT port")

    def _routing_table_add(self, node):
        i = 0
        infohash = self.torrent_info_hash
        infohash = infohash[:20]
        Alist = self._routing_table[infohash]
        for item in Alist:
            if node == item:
                i = 1
                
                break
        
        if i == 0:
            self._routing_table[infohash].append(node)
        print(self._routing_table)


    def ping(self, t, y, a=None, r=None):
        """
        TODO: implement the ping method
        :param t:
        :param y:
        :param a:
        :return:
        """
        if y == "q":
            self.action = "ping"
            ping = {"t":t, "y":y, "q":"ping", "a":a}
            print("\nping Query = " + str(ping))
            #print(ping)
            self.broadcast(ping, self_broadcast_enabled=True)
        elif y == "r":
            ping = {"t":t, "y":y, "q":"ping", "r":r}
            print("Response = " + str(ping))
            #print(ping)
            self.send_udp_message(ping, self.query_ip, self.query_port)

    def find_node(self, t, y, a=None, r=None):
        """
        TODO: implement the find_node method
        :return:
        """
        if(y == "q"):
            self.action = "find_node"
            Query = {"t":"aa", "y":y, "q":"find_node", "a": a}
            print("\nfind_node Query = " + str(Query))
            self.send_udp_message(Query, self.query_ip, self.query_port)
        elif (y == "r"):
            Response = {"t":"aa", "y":"r", "r": r}
            print("\nResponse = " + str(Response))          
            self.send_udp_message(Response, self.query_ip, self.query_port)

    def get_peers(self, t, y, a=None, r=None):
        """
        TODO: implement the get_peers method
        :return:
        """
        if(y == "q"):
            self.action = "get_peers"
            Query = {"t":"aa", "y":"q", "q":"get_peers", "a": a}
            print("\nget_peers Query = " + str(Query))
            #print(Query)
            self.send_udp_message(Query, self.query_ip, self.query_port)

        elif (y == "r"):
            Response = {"t":"aa", "y":"r", "r": r}
            print("\nResponse = " + str(Response))
            #print(Response)
            self.send_udp_message(Response, self.query_ip, self.query_port)

    def announce_peers(self, t, y, a=None, r=None):
        """
        TODO: implement the announce_peers method
        :return:
        """

        if(y == "q"):
            self.action = "announce_peers"
            Query = {"t":"aa", "y":"q", "q":"announce_peers", "a": a}
            print("\nannounce_peers Query = " + str(Query))
            #print(Query)
            self.send_udp_message(Query, self.query_ip, self.query_port)

        elif (y == "r"):
            Response = {"t":"aa", "y":"r", "r": r}
            print("\nannounce_peers Response = " + str(Response))
            #print(Response)
            self.send_udp_message(Response, self.query_ip, self.query_port)

    def process_query(self, query):

        data = dict(query)
        #q = data[b'q'].decode(('utf8'))
        y = data[b'y'].decode(('utf8'))
        #print(data[b'q'].decode(('utf8')))
        infohash = self.torrent.info_hash()
        infohash = infohash[:20]
        
        if self.action == "ping":
            
            #print("Response Query :" + str(query))

            #print(query)
            

            message = {"id" : self.nodeID, "info_hash" : infohash}
            self.get_peers("aa", "q", message)

        elif self.action == "find_node":
            print("Get node")

            message = {"id" : self.nodeID, "implied_port": 1, "info_hash" : infohash, "port" : self.DHT_PORT, "token" : self.token}
            self.announce_peers("aa", "q", message)


        elif self.action == "get_peers":
            Alist = []

            #print("Response get_peers: " + str(query))
            #print(query)
            r = dict(data[b'r'])

            token = r[b'token'] #Decode token
            self.token = token.decode(('utf8'))
            print(self.token)

            value = r[b'value']
            for item in value:
                #print(item[0].decode(('utf8')))
                node = (item[0].decode(('utf8')), item[1])
                Alist.append(node)

            #print(value)
            #print(Alist)
            message = {"id" : self.nodeID, "target" : infohash}
            self.find_node("aa", "q", message)


    def send_response(self, query):
        data = dict(query)
        q = data[b'q'].decode(('utf8'))
        y = data[b'y'].decode(('utf8'))
        #print(data[b'q'].decode(('utf8')))
        infohash = self.torrent.info_hash()
        infohash = infohash[:20]

        if q == "ping" and y == "q" :
            #self._routing_table
            
            #print("\nSending ping response")
            print("\n")

            node = (self.query_ip, self.query_port)
            self._routing_table_add(node)

            message = {"id": self.nodeID}
            self.ping("aa", "r",  None, message)

        elif q == "find_node" :
            node = (self.DHT_IP, self.DHT_PORT)
            message = {"id": self.nodeID, "nodes" : node}
            self.find_node("aa", "r", None, message)
        
        elif q == "get_peers":
            print("get_peers")
            message = {"id": self.nodeID, "token": "idk", "value": self._routing_table[infohash]}
            #print(message)
            #print("\nSending get_peers response")
            #print("\n")
            #message = {"id" : "abc", "info_hash" : infohash}
            self.get_peers("aa", "r", None, message)

        elif q == "announce_peers":
            print("announce_peer")
            message = {"id": self.nodeID}
            self.announce_peers("aa", "r", None, message)

    def set_total_uploaded(self, peer_id):
        """
        TODO: sets the total data uploaded so far by the peer passed as a parameter
        :param peer_id:
        :return: VOID
        """
        pass  # your code here

    def total_downloaded(self, peer_id):
        """
        TODO: sets the total data downloaded so far by the peer passed as a parameter
        :param peer_id:
        :return: VOID
        """
        pass  # your code here

    def validate_torrent_info_hash(self, peer_torrent_info_hash):
        """
        TODO: compare the info_hash generated by this peer with another info_hash sent by another peer
              this is done to make sure that both peers agree to share the same file.
        :param peer_torrent_info_hash: the info_hash from the info section of the torrent sent by other peer
        :return: True if the info_hashes are equal. Otherwise, returns false.
        """
        return 0



    def run(self):
        hash = self.server.host + str(self.server.port) + self.id
        sha1 = hashlib.sha1()
        sha1.update(hash.encode('utf8'))
        id = sha1.hexdigest()
        self.nodeID = id[:20]
        print("My Node ID : " + self.nodeID)

        node = (self.server.host, str(self.server.port))


        infohash = self._get_torrent_info_hash()
        self._routing_table[infohash] = []
        self._routing_table[infohash].append(node)
        



