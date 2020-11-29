import hashlib
from os import path
import shutil
from torrent import Torrent 



class FileManager:
    """
    The file manager class handles writes and reads from tmp, original and routing table.
    It also creates pointers to routing table, as well as read and write blocks/pieces of data.
    """
    TMP_FILE = "resources/tmp/ages.tmp"

    def __init__(self, torrent, peer_id):
        """
        Class constructor
        :param torrent:
        :param peer_id:
        """
        self.torrent = torrent
        self.peer_id = peer_id
        self.path = self.TMP_FILE
        self.path_to_original_file = None
        self.file_size = self.torrent.file_length()
        self.piece_size = self.torrent.piece_size()
        self.hash_info = self.torrent.info_hash()


    def create_tmp_file(self):
        """
        Creates a temporal file to flush the pieces. (i.e ages.tmp)
        :return:
        """
        with open(self.path, "wb") as out:
            out.truncate(self.file_size)

    def set_path_to_original_file(self, path):
        """
        set path to resources/shared/
        :param path:
        :return:
        """
        self.path_to_original_file = path

    def hash(self, data):
        """

        :param data:
        :return:
        """
        sha1 = hashlib.sha1()
        sha1.update(data)
        data_hashed = sha1.hexdigest()
        return data_hashed

    def get_block(self, piece_index, offset, length, path=None):
        """
        TODO: gets a block from the file in the path given as parameter
        :param piece_index: the index of the piece
        :param offset: the begin offset of the block in that piece
        :param length: the length of the block
        :param path: Note that paths may be only the original file (i.e ages.txt) or
                     the tmp file (i.e ages.tmp)
        :return:
        """
        theFile = open(path)
        target = piece_index * self.piece_size
        target += offset
        theFile.seek(target)

        block = theFile.read(length)
        # your code here
        return block

    def get_piece(self, blocks):
        """
        TODO: Converts a list of blocks in a piece
        :param blocks: a list of blocks
        :return: the piece
        """
        

        piece = ""
        for i in range(len(blocks)):
            piece += str(blocks[i])
        # your code here
        return piece

    def flush_block(self, piece_index, block_index, block, path="blocks.data"):
        """
        TODO: writes a block in blocks.data
              Each entry in routing table has the following format:
              <pointer><delimiter><block>
              pointer: A SHA1 hash of the hash info of the torrent file, piece index and block index
              delimiter: $$$
              block: the data of the block

        :param piece_index:
        :param block_index:
        :param block:
        :return: VOID
        """
        try:

            theFile = open("blocks.data", "r+")
        except:
            theFile = open("blocks.data", "w+")
        
        i = 0
        #print(theFile.seek(0, 2))
        theFile.seek(0, 2)
        #theFile.write("\n")

        pointer = self.pointer(self.hash_info, piece_index, block_index)
        #print(pointer.decode("UTF-8"))
        pointer = pointer.decode("UTF-8")
        theFile.write(pointer)
        theFile.write("$$$")
        theFile.write(block)
        theFile.write("\n")
        #print(theFile.seek(0, 2))
        theFile.close()
        #theFile.flush()

        


    def pointer(self, hash_info, piece_index, block_index):
        """
        Creates a pointer for a specific block
        :param hash_info:
        :param piece_index:
        :param block_index:
        :return:
        """
        data = str(piece_index) + str(block_index) + hash_info
        data_encoded = str.encode(data)
        return str.encode(self.hash(data_encoded))

    def flush_piece(self, piece_index, piece):
        """
        TODO: write a piece in tmp file once the piece is validated with the hash of the piece
        :param piece_index:
        :param piece:
        :return: VOID
        """
        try:

            theFile = open(self.path, "r+")
        except:
            theFile = open(self.path, "w+")
        #theFile = open(self.path, "r+")
        #theFile.seek(0, 2)
        #print(theFile.read(2048))

        #print(self.piece_validated(piece, piece_index))

        if self.piece_validated(piece, piece_index):
            
            theFile.seek(piece_index * self.piece_size)
            
            theFile.write(piece)
            #theFile.seek(0, 2)

        #theFile.seek(0)
        #x = theFile.read(self.piece_size)
        
        #print(self.piece_validated(x, 0))

        
        theFile.close()

        #if self.piece_validated(piece, piece_index):
            #theFile = open()
        

    def get_pointers(self, hash_info, piece_index):
        """
        TODO: gets all the pointers representing a piece in the routing table
        :param hash_info:
        :param piece_index:
        :return: a list of pointers to the blocks in the same piece
        """
        theFile = open("blocks.data", 'r')
        
        #while theFile.next():
        aList = theFile.readlines()
        returnList = []
        for i in range(len(aList)):
            target = aList[i].split('$$$')
            print(target[0])
            returnList.append(target[0])


        return returnList

        #try:
          #  while theFile.next():
          #      print(theFile.next())
       # except:
            #theFile.close()
            
            
        #return 0 # your code here

    def extract_piece(self, piece_index):
        """
        TODO: extract a piece from the routing table once all the blocks from that piece are completed
        :param piece_index:
        :return: the piece
        """
        piece = ""
        index = piece_index * 8

        theFile = open("blocks.data", 'r')
        aList = theFile.readlines()
        for i in range(8):
            target = aList[index].split('$$$')
            #print(target[1])
            piece += str(target[1]).rstrip()
            index += 1

        # your code here
        return piece

    def piece_offset(self, piece_index):
        """
        :param piece_index:
        :return:
        """
        return piece_index * self.piece_size

    def block_offset(self, block_index, block_length):
        """
        :param block_index:
        :param block_length:
        :return:
        """
        return block_index * block_length

    def block_index(self, begin):
        return int(begin/self.torrent.block_size())

    def piece_validated(self, piece, piece_index):
        hashed_torrent_piece = self.torrent.piece(piece_index)
        hashed_piece = self.hash(piece.encode())
        return hashed_torrent_piece == hashed_piece

    def move_tmp_to_shared(self):
        """
        Moves the tmp file once all the pieces from that file are downloaded to the shared folder
        :return:
        """
        file_shared_path = "resources/shared/" + self.torrent.file_name()
        if not path.exists(file_shared_path):
            shutil.move(self.path, file_shared_path)

    def path_exist(self, path_to_file):
        return path.exists(path_to_file)

    def run(self):
        loop = int(self.piece_size/2048)
        print(loop)
        blockList = []
       #self.create_tmp_file()
        self.set_path_to_original_file("age.txt")
       # with open("age.txt") as f:
        for count in range(loop):
            offset = self.block_offset(count, 2048)
            block_index = self.block_index(offset)
            print(block_index)
            block = self.get_block(0, offset, 2048, self.path_to_original_file)
            self.flush_block(0, block_index, block)
            blockList.append(block)


        #print(blockList)
        print(len(blockList))
        piece = self.get_piece(blockList)
       # print(piece)
        print(self.piece_validated(piece, 0))
        self.flush_piece(0, piece)
        pointers = self.get_pointers(self.hash_info, 0)
        print(pointers)
        thePiece = self.extract_piece(0)
        print(thePiece)
        print(self.piece_validated(thePiece, 0))
      # print(self.hash(str(block).encode()))
      # self.flush_block(0, 0, block)
       #print(self.piece_offset(2))
      # print(type(self.torrent.block_size()))
      # print(self.block_index(2048))
      # print(self.piece_offset(1))
      # print(self.torrent.piece(0))

       #piece = open("age.txt")
        
       # print(piece)
        #print(self.torrent.piece(0))
       # hashe = self.hash(piece)
       # print(hashe)
                

        #self.create_tmp_file()


if __name__ == '__main__':
    torrent = Torrent("age.torrent")
    test = FileManager(torrent, "abc")
    test.run()

"""
class FileManager:

   
   # This class implements all the methods needed to access the tmp, routing table and the original file (if seeder)
   # including all the methods to read and flush blocks.
    

    def __init__(self, torrent, peer_id):
        """

      #  :param torrent: The torrent object
      #  :param peer_id:
       
      #  pass

   


