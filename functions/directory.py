import math
import pickle

from variables import *
from inode import IndexNode
from control import *

class Directory:
    def __init__(self, superblock):
        self.control = Control(superblock)

    def mkdir(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        if len(args) != 1: raise WrongParameters
        dir = args[0].split('/')
        if dir[-1] in ['.', '..', '', ' ']: raise NotAcceptableDirName
        cwd = self.control.change_dir(file, cwd[0], dir[0:-1], inodes_array)
        folder = self.control.create_folder(file, dir[-1], inodes_array, inodes_bitmap, cwd, blocks_bitmap)
        self.control.add_in_folder(file, folder, inodes_array, cwd, blocks_bitmap)

    def rmdir(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        if len(args) != 1: raise WrongParameters
        dir = args[0].split('/')
        if dir[-1] in ['.', '..']: raise CantRemove
        cwd = self.control.change_dir(file, cwd[0], dir, inodes_array)
        folder_dict = self.control.read_blocks(file, cwd)
        if len(folder_dict) == 2:
            for block in cwd.block_pointers:
                blocks_bitmap[block] = 0
            inodes_bitmap[cwd.index] = 0
            cwd = self.control.read_inode(inodes_array, folder_dict['..'])
            folder_dict = self.control.read_blocks(file, cwd)
            del folder_dict[dir[-1]]
            self.control.save_bitmap(file, blocks_bitmap, inodes_bitmap)
            self.control.rewrite(file, cwd, inodes_array, folder_dict, blocks_bitmap)

    def ls(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        if len(args) != 0 and len(args) != 1: raise WrongParameters
        dir = args[0].split('/') if len(args) != 0 else []
        cwd = self.control.change_dir(file, cwd[0], dir[0:-1], inodes_array)
        folder_dict = self.control.read_blocks(file, cwd)
        print(folder_dict)        

    def cd(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        if len(args) != 1: raise WrongParameters
        dir = args[0].split('/')
        cwd[0] = self.control.change_dir(file, cwd[0], dir, inodes_array)
