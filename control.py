import pickle
import math
import copy
import time
from bitarray import bitarray
import numpy as np

from inode import IndexNode
from variables import *
from exceptions import *

class Control:
    def __init__(self, superblock):
        self.sb = superblock

    def save_bitmap(self, f, blocks_bitmap=None, inodes_bitmap=None):
        """Salvar Bitmaps dentro do disco"""
        # <-::- Save Blocks Bitmap -::->
        if blocks_bitmap:
            f.seek(self.sb['blocks_bitmap_start'] * self.sb['block_size'])
            f.write(bitarray(blocks_bitmap).tobytes().ljust((self.sb['inodes_bitmap_start'] - self.sb['blocks_bitmap_start']) * self.sb['block_size'], b'\x00'))

        # <-::- Save INodes Bitmap -::->
        if inodes_bitmap:
            f.seek(self.sb['inodes_bitmap_start'] * self.sb['block_size'])
            f.write(bitarray(inodes_bitmap).tobytes().ljust((self.sb['data_blocks_start'] - self.sb['inodes_bitmap_start']) * self.sb['block_size'], b'\x00'))

    def save_inode(self, inodes_array, inode):
        inodes_array[inode.index] = inode
        np.save('inodes.npy', inodes_array)

    def read_blocks(self, f, inode, inodes_array):
        s = b''
        if inode.inode_pointer:
            inode = self.read_inode(inodes_array, inode.inode_pointer)
        for block in inode.block_pointers:
            f.seek((self.sb['data_blocks_start'] + block) * self.sb['block_size'])
            s += f.read(self.sb['block_size'])
        return pickle.loads(s)

    def divide_in_blocks(self, content):
        """Retorna uma tupla com tamanho, numero de blocos e vetor com os conteúdos divididos pelos blocos necessários já completos e serializados (size, blocks, [contents])"""
        serialized_content = pickle.dumps(content)
        serialized_content_size = len(serialized_content)
        total_blocks = math.ceil(serialized_content_size / self.sb['block_size'])
        serialized_content = serialized_content.ljust(total_blocks * self.sb['block_size'], b'\x00')
        contents = []
        for start in range(total_blocks):
            end = start + 1
            contents.append(serialized_content[start * self.sb['block_size'] : end * self.sb['block_size']])
        return (serialized_content_size, total_blocks, contents)

    def rewrite(self, f, inode, inodes_array, new_content, blocks_bitmap):
        size, blocks, serialized_contents = self.divide_in_blocks(new_content)
        for block in inode.block_pointers:
            blocks_bitmap[block] = 0
        blocks = self.find_empty_place(blocks_bitmap, self.sb['usable_blocks'], blocks)
        inode.block_pointers = blocks
        for block, content in zip(blocks, serialized_contents):
            blocks_bitmap[block] = 1
            # <-::- Gravar blocos -::->
            f.seek((self.sb['data_blocks_start'] + block) * self.sb['block_size'])
            f.write(content)
        # <-::- Salvar Bitmap dos Blocos -::->
        self.save_bitmap(f, blocks_bitmap)
        
        # <-::- Salvar INodes -::->
        self.save_inode(inodes_array, inode)

    def read_inode(self, inodes_array, inode_index):
        return inodes_array[inode_index]

    def find_empty_place(self, bitmap, limit, times):
        """Retorna vetor de índices livres no Bitmap de entrada"""
        indexes = []
        for index in range(limit):
            if bitmap[index] == 0:
                indexes.append(index)
            if times == len(indexes): 
                for index in indexes:
                    bitmap[index] = 1
                return indexes
        raise FullBitmap('O bitmap está cheio!')

    def add_in_folder(self, f, inode, inodes_array, folder, blocks_bitmap):
        folder_dict = self.read_blocks(f, folder, inodes_array)
        folder_dict[inode.name] = inode.index

        self.rewrite(f, folder, inodes_array, folder_dict, blocks_bitmap)

    def change_dir(self, f, cwd, dirs, inodes_array):
        if len(dirs) == 0: return cwd
        if dirs[0] == '':
            cwd = inodes_array[0]
            dirs.pop(0)
        for dir in dirs:
            cwd = self.read_inode(inodes_array, self.read_blocks(f, cwd, inodes_array)[dir])
            if cwd.permissions[0] != 'd':
                raise NotFolderINode
        return cwd
    
    def create_folder(self, f, name, inodes_array, inodes_bitmap, folder, blocks_bitmap):
        inode_index = (self.find_empty_place(inodes_bitmap, self.sb['inodes'], 1))[0]
        inode = IndexNode(name, inode_index, 'Theo', 'Theo', 0, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), 'drwxr-xr-x')
        folder_content = {'.':inode_index, '..':folder.index}
        self.add_in_folder(f, inode, inodes_array, folder, blocks_bitmap)
        self.rewrite(f, inode, inodes_array, folder_content, blocks_bitmap)
        self.save_bitmap(f, inodes_bitmap=inodes_bitmap)
        return inode

    def create_file(self, f, name, inodes_array, inodes_bitmap, folder, blocks_bitmap, content=''):
        inode_index = (self.find_empty_place(inodes_bitmap, self.sb['inodes'], 1))[0]
        inode = IndexNode(name, inode_index, 'Theo', 'Theo', 0, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), '-rwxr-xr-x')
        file_content = content
        self.add_in_folder(f, inode, inodes_array, folder, blocks_bitmap)
        self.rewrite(f, inode, inodes_array, file_content, blocks_bitmap)
        self.save_bitmap(f, inodes_bitmap=inodes_bitmap)
        return inode
    
    def create_link_inode(self, name, org_inode, inodes_bitmap):
        inode_index = (self.find_empty_place(inodes_bitmap, self.sb['inodes'], 1))[0]
        inode = copy.deepcopy(org_inode)
        inode.name = name
        inode.index = inode_index
        inode.block_pointers = []
        inode.inode_pointer = org_inode.index
        return inode