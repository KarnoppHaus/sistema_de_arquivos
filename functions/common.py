import math
import pickle

from variables import *
from inode import IndexNode
from control import *

class Common:
    def __init__(self, superblock):
        self.control = Control(superblock)

    def mv(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        pass
        
    def ln(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        pass
