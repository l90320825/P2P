"""
Copy and paste here your code implementation from pwp.py file
"""

from message import Message

class PWP:
    def __init__(self, peerid, infohash):
        self.message = Message()
        self.peerid = peerid
        self.infohash = infohash



    def get_handshake(self): #prepare handshake message
        self.message.handshake['info_hash'] = self.infohash 
        self.message.handshake['peer_id'] = self.peerid
        return self.message.handshake
        