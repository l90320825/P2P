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
    # Shouldn't DHT_IP be "" for it to use the IPv4 given by router? - Chun
    #DHT_IP = "127.0.0.2"

    def __init__(self,peer, server, torrent, announce=False):
        self.server = server
        self.peer = peer
        self.torrent = torrent
        self.torrent_info_hash = self._get_torrent_info_hash()
        self.announce = announce

        self.DHT_IP = self.server.host
        self.server_port = self.server.port

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

        # self.swarm = []

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
        return self.torrent.info_hash()
        # encoded_hash = self.encode(self.torrent.info_hash)
        # torrent_info_sha1_hash = hashlib.sha1(encoded_hash)
        # return torrent_info_sha1_hash  # returns the info hash

    # def add_peer_to_swarm(self, peer_id, peer_ip, peer_port):
    #     """
    #     TODO: when a peers connects to the network adds this peer
    #           to the list of peers connected
    #     :param peer_id:
    #     :param peer_ip:
    #     :param peer_port:
    #     :return:
    #     """
    #     peer = {"id": peer_id, "ip": peer_ip, "port": peer_port}
    #     self.swarm.append(peer)
    #
    # def remove_peer_from_swarm(self, peer_id):
    #     """
    #     TODO: removes a peer from the swarm when it disconnects from the network
    #           Note: this method needs to handle exceptions when the peer disconnected abruptly without
    #           notifying the network (i.e internet connection dropped...)
    #     :param peer_id:
    #     :return:
    #     """
    #     try:
    #         for peer in self.swarm:
    #             if peer["id"] == peer_id:
    #                 self.swarm.remove(peer)
    #     except Exception as e:
    #         print(e)

    def get_DHT(self, info_hash):
        return self._routing_table[info_hash]

    def remove_peer_from_DHT(self, peer_id):
        try:
            for peer in self._routing_table:
                if peer["id"] == peer_id:
                    self._routing_table.remove(peer)
        except Exception as e:
            print(e)

    def encode(self, message):
        """
        bencodes a message
        :param message: a dictionary representing the message
        :return: the bencoded message
        """
        #print("SOMETHING")
        encoded_message = bencodepy.encode(message)
        #print("SOMETHING SOMETHING")
        return encoded_message

    def decode(self, bencoded_message):
        """
        Decodes a bencoded message
        :param bencoded_message: the bencoded message
        :return: the original message
        """
        # This works for Windows, but not Mac. Got a solution?
        # bc = bencodepy.Bencode(encoding='utf-8')
        # return bc.decode(bencoded_message)

        return bencodepy.decode(bencoded_message)

    def broadcast(self, message, self_broadcast_enabled=False):
        """
        TODO: broadcast the list of connected peers to all the peers in the network.
        :return:
        """
        try:
            print("Broadcast_Message: ", message)
            encoded_message = self.encode(message)
            print("bencoded = " + encoded_message.decode('utf-8') + "\n")
            self.udp_socket.sendto(encoded_message, ('<broadcast>', self.DHT_PORT))
            print("Message broadcast.....")
        except socket.error as error:
            print(error)

    def send_udp_message(self, message, ip, port):
        try:
            # new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = self.encode(message)
          #  print("bencoded = " + message.decode('utf8') + "\n")
            # new_socket.sendto(message, (ip, port))
            self.udp_socket.sendto(message, (ip, port))
          #  print("Sent!")
        except:
            print("error")

    def broadcast_listener(self):
        try:
            print("Listening at DHT port: ", self.DHT_PORT)
            while True:
                raw_data, sender_ip_and_port = self.udp_socket.recvfrom(4096)
                # print("Received Data")
                # print(self.DHT_IP !=  sender_ip_and_port[0])
                if raw_data and self.DHT_IP != sender_ip_and_port[0]:
                    data = self.decode(raw_data)
                    # pickle.loads(data)
                    # data = dict(data)
                    # print(data[b't'].decode(('utf8')))
                    # for key, item in data.items():
                    #  print(key.decode(('utf8')))
                    # print(data)
                    # self.process_query(data)
                    ip_sender = sender_ip_and_port[0]
                    port_sender = sender_ip_and_port[1]
                    self.query_ip = ip_sender
                    self.query_port = port_sender

                    if data[b'y'].decode('utf8') == "r":
                        # You got a response
                        self.process_response(data)
                    else:
                        # You got a query
                        self.send_response(data)

                    # print("Data received by sender", data, ip_sender, port_sender)
                    # node = (ip_sender, port_sender)
                    # self._routing_table_add(node)

        except:
            print("Error listening at DHT port")

    def _routing_table_add(self, node):
        i = 0
        infohash = self.torrent_info_hash
        print("Info_hash: ", infohash)
        # infohash = infohash[:20]
        try:
            Alist = self._routing_table[infohash]
            for item in Alist:
                if node == item:
                    i = 1
                    break
            if i == 0:
                self._routing_table[infohash].append(node)

            self.peer.swarm = self._routing_table
            print("DHT: ", self._routing_table)
        except:
            self._routing_table[infohash] = []
            self._routing_table[infohash].append(node)
            self.peer.swarm = self._routing_table[infohash]

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
            ping = {"t": t, "y": y, "q": "ping", "a": ""}
          #  print("\nping Query = " + str(ping))
            # print(ping)
            self.broadcast(ping, self_broadcast_enabled=True)
        elif y == "r":
            ping = {"t": t, "y": y, "q": "ping", "r": r}
         #   print("Response = " + str(ping))
            # print(ping)
            self.send_udp_message(ping, self.query_ip, self.query_port)

    def find_node(self, t, y, a=None, r=None):
        """
        TODO: implement the find_node method
        :return:
        """
        if (y == "q"):
            self.action = "find_node"
            Query = {"t": "aa", "y": y, "q": "find_node", "a": a}
        #    print("\nfind_node Query = " + str(Query))
         #   print("Query IP: ", self.query_ip)
        #    print("Query Port: ", self.query_port)
            # ip, port = a['target']
            self.send_udp_message(Query, self.query_ip, self.query_port)
        elif (y == "r"):
            Response = {"t": "aa", "y": y, "q": "find_node", "r": r}
         #   print("\nResponse = " + str(Response))
            self.send_udp_message(Response, self.query_ip, self.query_port)

    def get_peers(self, t, y, a=None, r=None):
        """
        TODO: implement the get_peers method
        :return:
        """
        if (y == "q"):
            self.action = "get_peers"
            Query = {"t": t, "y": "q", "q": "get_peers", "a": a}
         #   print("\nget_peers Query = " + str(Query))
            # print(Query)
            self.send_udp_message(Query, self.query_ip, self.query_port)

        elif (y == "r"):
            Response = {"t": t, "y": "r", "q": "get_peers", "r": r}
        #    print("\nget_peers Response = " + str(Response))
            # print(Response)
        #    print("Sending to: ", self.query_ip, self.query_port)
            self.send_udp_message(Response, self.query_ip, self.query_port)

    def announce_peers(self, t, y, a=None, r=None):
        """
        TODO: implement the announce_peers method
        :return:
        """

        if (y == "q"):
            self.action = "announce_peers"
            Query = {"t": "aa", "y": "q", "q": "announce_peers", "a": a}
        #    print("\nannounce_peers Query = " + str(Query))
            # print(Query)
            self.send_udp_message(Query, self.query_ip, self.query_port)

        elif (y == "r"):
            Response = {"t": "aa", "y": "r", "q": "announce_peers", "r": r}
        #    print("\nannounce_peers Response = " + str(Response))
            # print(Response)
            # print("Query IP: ", self.query_ip)
            # print("Query Port: ", self.query_port)
            self.send_udp_message(Response, self.query_ip, self.query_port)

    def process_response(self, query):
        #print(query)
        data = dict(query)
        #print(data)
        q = data[b'q'].decode('utf-8')
        # y = data[b'y'].decode(('utf8'))
        # print("q: ", q)
        infohash = self.torrent.info_hash()
        # infohash = infohash[:20]

        if q == "ping":
            # print("Response Query :" + str(query))
            # print(query)

            message = {"id": self.nodeID, "info_hash": infohash}
            self.get_peers("aa", "q", message)

        elif q == "find_node":
        #    print("Get node")
            message = {"id": self.nodeID, "implied_port": 1, "info_hash": infohash, "port": self.DHT_PORT,
                       "token": self.token}
            self.announce_peers("aa", "q", message)

        elif q == "get_peers":
            Alist = []

        #    print("Response get_peers: " + str(query))
            # print(query)
            r = dict(data[b'r'])

            token = r[b'token']  # Decode token
            self.token = token.decode(('utf8'))
            #print("token: ", self.token)

            # value = r[b'value']
            # for item in value:
            #     # print(item[0].decode(('utf8')))
            #     node = (item[0].decode(('utf8')), item[1])
            #     Alist.append(node)

            #print("r[id]: ", r[b'id'].decode('utf-8'))
            #print("r['nodes']: ", r[b'nodes'])

            for node in r[b'nodes']:
        #        print("Node: ", node.decode('utf-8'))
                message = {"id": r[b'id'].decode('utf-8'), "target": node.decode('utf-8')}
                self.find_node("aa", "q", message)

        elif q == "announce_peers":
            # message = {"id": self.info_hash}
            # print("ADD TO DHT")
            # print("Add to Routing Table: ", data[b'r'][b'id'].decode('utf-8'))
            print("Add to Routing Table: ", (self.query_ip, self.query_port))
           
            # self._routing_table_add(data[b'r'][b'id'].decode('utf-8'))
            self._routing_table_add((self.query_ip, self.query_port))

    def send_response(self, query):
        data = dict(query)
        q = data[b'q'].decode(('utf8'))
        t = data[b't'].decode(('utf8'))
        # y = data[b'y'].decode(('utf8'))
        # print(data[b'q'].decode(('utf8')))
        infohash = self.torrent.info_hash()
        infohash = infohash[:20]

        if q == "ping":
            # self._routing_table
            # print("\nSending ping response")
            print("\n")
            message = {"id": self.nodeID}
            self.ping(t, "r", None, message)

        elif q == "find_node":
     #       print("Process find_node Query")
     #       print("Data: ", data)
     #       print("Node: ", data[b'a'][b'target'].decode('utf-8'))
            node = data[b'a'][b'target'].decode('utf-8')
            message = {"id": self.nodeID, "target": node}
            self.find_node("aa", "r", None, message)

        elif q == "get_peers":
    #        print("get_peers")
            nodes = []
            # print("Torrent_info: ", self.torrent_info_hash)
            # print("Raw Data info hash: ", data[b'a'][b'info_hash'])
            decoded_info_hash = data[b'a'][b'info_hash'].decode('utf-8')
            # print("Data info hash: ", decoded_info_hash)

            if self.torrent_info_hash == decoded_info_hash:
                # print("Hello?")
                nodes.append(self.nodeID)
                # print("Append Self: ", self.nodeID)
            for node in self._routing_table:
                # print("Hello????")
                if node[b'info_hash'].decode('utf-8') == data[b'a'][b'info_hash'].decode('utf-8'):
                    nodes.append(node)
                    # print("Append DHT Node")
            # print("I'm here!")
            message = {"id": self.nodeID, "token": "idk", "nodes": nodes}
            # print("I'm here now!")
            # print(message)
            # print("\nSending get_peers response")
            # print("\n")
            # message = {"id" : "abc", "info_hash" : infohash}
            self.get_peers("aa", "r", None, message)

        elif q == "announce_peers":
            print("announce_peer")
            message = {"id": self.nodeID, "server_port": self.server_port}
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
        hash = str(self.server.host) + str(self.server.port) + str(self.id)
        sha1 = hashlib.sha1()
        sha1.update(hash.encode('utf8'))
        id = sha1.hexdigest()
        self.nodeID = id[:20]
        print("My Node ID : " + self.nodeID)

        node = (self.server.host, str(self.server.port))

        infohash = self._get_torrent_info_hash()
        #self._routing_table[infohash] = []
        #self._routing_table[infohash].append(node)
        threading.Thread(target=self.broadcast_listener).start()
        if self.announce:
            self.ping("aa", "q")
        #print("Tracker DHT Origin -> Info_Hash: ", self.get_DHT(self.torrent.info_hash()))
