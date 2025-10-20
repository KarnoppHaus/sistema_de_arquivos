import math
import pickle

from variables import *
from inode import IndexNode
from control import *

# <-::- FUNÇÕES DE ARQUIVOS -::->

class Archives():
    def __init__(self, superblock):
        self.control = Control(superblock)

    def touch(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        pass

    def rm(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        pass

    def echo(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        pass

    def cat(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        pass

    def cp(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        pass