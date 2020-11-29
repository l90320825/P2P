import threading
from file_manager import FileManager
from htpbs import ProgressBars


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
        self.file_manager = FileManager(self.torrent, self.peer_id)
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

        progressbars = ProgressBars(num_bars=1)

        self.file_manager.create_tmp_file()







        while pieceIndex < self.torrent.num_pieces():
            progressbars.set_bar_prefix(bar_index=0, prefix="Downloads: <Piece " + str(pieceIndex) + " :")
            progress = 12.5

            for i in range(8): # Download first piece
                data = self.client.message.request
                data['index'] = pieceIndex
                data['begin'] = self.torrent.block_size() * i
                data['length'] = self.torrent.block_size()

                self.client.send(data)
                data = self.client.receive()
                #print(data)
            
                blockIndex = self.file_manager.block_index(data['begin'])
                self.file_manager.flush_block(data['index'],  blockIndex, data['block'])
                progress += 12.5
                progressbars.update(bar_index=0, value=progress)

                
            thePiece = self.file_manager.extract_piece(pieceIndex)
            #print(thePiece)
            print(self.file_manager.piece_validated(thePiece ,pieceIndex))

            if(self.file_manager.piece_validated(thePiece ,pieceIndex)):
                print(self.file_manager.piece_validated(thePiece ,pieceIndex))
                self.file_manager.flush_piece(pieceIndex, thePiece)
            print(self.file_manager.piece_validated(thePiece ,pieceIndex))
            missBitIndex = self.client.message.next_missing_piece_index()
            missBitBlock = self.client.message.next_missing_block_index(missBitIndex)
            self.client.message._bitfield['bitfield'][missBitIndex][missBitBlock] = True
            print(self.client.message._bitfield['bitfield'][missBitIndex])
            pieceIndex += 1
            progressbars.finish()


        

        
        print(self.client.message._bitfield['bitfield'])

