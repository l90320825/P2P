import pickle
from file_manager import FileManager
from config import Config
from message import Message
from torrent import Torrent
from htpbs import ProgressBars, Work
import time # required for demonstration purposes only


class Uploader:

    def __init__(self, peer_id, server, peer_uploader, address, torrent):
        self.peer_id = peer_id
        self.config = Config()
        self.torrent = torrent
        self.file_manager = FileManager(torrent, peer_id)
        self.peer_uploader = peer_uploader
        self.server = server
        self.address = address
        self.peer_id = -1
        self.uploaded = 0  # bytes
        self.downloaded = 0  # bytes
        self.message = Message() #Send message

        #### implement this ####
        self.uploader_bitfield = None
        self.downloader_bitfield = None

    def send(self, data):
        serialized_data = pickle.dumps(data)
        self.peer_uploader.send(serialized_data)

    def receive(self, max_alloc_mem=4096):
        serialized_data = self.peer_uploader.recv(max_alloc_mem)
        data = pickle.loads(serialized_data)
        return data

    def work(self, progressbars, bar_index, work_value, work_name, uploadeder):
       
        """
        :param progressbars: the progressbar obkect
        :param bar_index: a integer representing the index of the bae
        :param work_value: a value for time.sleep() to simulate different progress bars rates
        :param work_name: the name of the work
        :return: VOID
        """

        progressbars.set_bar_prefix(bar_index=bar_index, prefix=work_name)
        progressbars.set_bar_suffix(bar_index=bar_index, suffix=" >")

        for i in range(101):
             # your work here. we use the time.sleep() as example
             # Real work could be downloading a file and show progress
             time.sleep(work_value)
             
             data = uploadeder.receive()
            # block = uploadeder.file_manager.get_block(data['index'], data['begin'], uploadeder.torrent.block_size(), uploadeder.file_manager.path_to_original_file)
            # package = uploadeder.message.piece
            # package['index'] = data['index']
            # package['begin'] = data['begin']
            # package['block'] = block
             uploadeder.send(i)
             progressbars.update(bar_index=bar_index, value=i)

        progressbars.finish()



    def run(self):
        self.file_manager.set_path_to_original_file("age.txt")
       # block = self.file_manager.get_block(0, 0, self.torrent.block_size(), self.file_manager.path_to_original_file)
       # package = self.message.piece
       # package['index'] = 0
       # package['begin'] = 0
       # package['block'] = block
        #self.send(package)
        

        # start with 3 bars
        #progressbars = ProgressBars(num_bars=1)
        # set bar #3 to be the total progress
        #progressbars.set_last_bar_as_total_progress(prefix="Total: ")

        # start all the threaded works
       # Work.start(self.work, (progressbars, 0, 0.1, "<Piece 0 : ", self))
        #Work.start(self.work, (progressbars, 1, 0.01, "w2: "))
        index = 0

        print("running uploader")

        while True:

           # progressbars.set_bar_prefix(bar_index=0, prefix="<Piece " + str(index) + " :")
            w = 12.5
            for i in range(8):
            
                #time.sleep(0.1)
                data = self.receive()
                
                block = self.file_manager.get_block(data['index'], data['begin'], self.torrent.block_size(), self.file_manager.path_to_original_file)
                package = self.message.piece
                package['index'] = data['index']
                package['begin'] = data['begin']
                package['block'] = block

                print(package)
                self.send(package)            
                w += 12.5
               # progressbars.update(bar_index=0, value=w)

           # progressbars.finish()
            index += 1

    """   
        while True:
            data = self.receive()
            print(data)
            block = self.file_manager.get_block(data['index'], data['begin'], self.torrent.block_size(), self.file_manager.path_to_original_file)
            package = self.message.piece
            package['index'] = data['index']
            package['begin'] = data['begin']
            package['block'] = block
            self.send(package)

    """
