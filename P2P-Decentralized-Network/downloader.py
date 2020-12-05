import threading
from file_manager import FileManager
from htpbs import ProgressBars
import time
import pickle


class Downloader:

    def __init__(self, peer_downloader, peer_id, torrent, interested, keep_alive, client):
        self.client = client
        
        self.peer_downloader = peer_downloader
        self.peer_id = peer_id
        self.torrent = torrent
        self.uploader_id = -1  # not know until the downloader runs.
        self.info_hash = self.torrent.info_hash()
        self.alive = keep_alive
        self.interested = interested
        
        self.bitfield_lock = threading.Lock()
        self.file_lock = threading.Lock()





    def run(self):
        """
        while True:
            data = self.client.receive()
        """


        pieceIndex = 0
        missBitIndex = 0
        missBitBlock = 0
        progress = 0
        theIdex = 0
        #progressbars = ProgressBars(num_bars=2)

        

        #print(self.peer_downloader.getsockname)

        blocksize = self.torrent.block_size() 

        #print(self.client.message._bitfield['bitfield'])

        







        #while pieceIndex < 5: #self.torrent.num_pieces():
        while self.client.message.next_missing_piece_index() != -1 : #Find any missing piece
            
            progress = 12.5 # 100% / 8
            blockList = []

            self.bitfield_lock.acquire() #Access bitfield
            missBitIndex = self.client.message.next_missing_piece_index()
            missBitBlock = self.client.message.next_missing_block_index(missBitIndex)
            theIdex =  (missBitIndex * 8) + missBitBlock
            if self.client.id == 0:
                self.client.peer.progressbars.set_bar_prefix(bar_index=self.client.id, prefix="Downloads: <Piece " + str(theIdex) + " :")
            else:
                self.client.peer.progressbars.set_bar_prefix(bar_index=self.client.id, prefix=" Piece " + str(theIdex) + " :")
            self.client.message._bitfield['bitfield'][missBitIndex][missBitBlock] = True #Set the bit to true first, so other client thread cant download the same block
            self.bitfield_lock.release()
            w = 0


            for i in range(8): #Loop 8 times for 8 blocks in a piece
                data = self.client.message.request
                data['index'] = theIdex
                data['begin'] = 2048 * i
                data['length'] = 2048

               
               
                

                self.client.send(data)
                data = self.client.receive()
                blockIndex = int(data['begin'] / 2048)
            
                #blockIndex = self.client.peer.file_manager.block_index(data['begin'])

                self.file_lock.acquire()
                self.client.file_manager.flush_block(data['index'],  blockIndex, data['block'])
                blockList.append(data['block'])
                self.file_lock.release()


                progress += 12.5
                w += 1
                self.client.peer.progressbars.update(bar_index=self.client.id, value=progress)


            

                
            self.file_lock.acquire()    
            #thePiece = self.client.file_manager.extract_piece(theIndex)
            thePiece = self.client.file_manager.get_piece(blockList)
            self.file_lock.release()

           # print(thePiece)

            #print(thePiece)
            #print(self.file_manager.piece_validated(thePiece ,pieceIndex))

            if(self.client.file_manager.piece_validated(thePiece , theIdex)): #If the piece is correct, flush piece
                #print(self.client.file_manager.piece_validated(thePiece , missBitBlock))

                self.file_lock.acquire()
                self.client.file_manager.flush_piece(theIdex, thePiece)
                self.file_lock.release()

            else: #If the piece is wrong, set bitfield back to False
              #  print(self.client.file_manager.piece_validated(thePiece , pieceIndex))

                self.bitfield_lock.acquire()
                self.client.message._bitfield['bitfield'][missBitIndex][missBitBlock] = False
                self.bitfield_lock.release()


           # print(self.client.file_manager.piece_validated(thePiece , theIdex))
            """
            missBitIndex = self.client.message.next_missing_piece_index()
            missBitBlock = self.client.message.next_missing_block_index(missBitIndex)
            self.client.message._bitfield['bitfield'][missBitIndex][missBitBlock] = True
            """
            #print(self.client.message._bitfield['bitfield'][missBitIndex])
            pieceIndex += 1
            #print(blockList)
            #self.client.peer.progressbars.finish()


        

        #thePiece = self.client.file_manager.extract_piece(1)
       # print(thePiece)
       # print(theIdex)
       
        #print(self.client.file_manager.piece_validated(thePiece , 1))
        #self.client.file_manager.piece_validated(thePiece , 1)
        #print(self.client.message._bitfield['bitfield'])

        #print(self.client.torrent.num_pieces())
        #print((theIdex + 1))
        #self.client.peer.progressbars.clear_bar(bar_index=self.client.id)
        #self.client.peer.progressbars.set_hidden_bars(bar_index=self.client.id)
        time.sleep(5)
        self.client.peer.progressbars.finish_all()
        






        if (theIdex + 1) == self.client.torrent.num_pieces():
            self.client.file_manager.move_tmp_to_shared()

