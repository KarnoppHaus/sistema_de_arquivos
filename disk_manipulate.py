from variables import *
import pickle
from bitarray import bitarray
from inode import IndexNode
import time
import numpy as np

def create():
    with open('disk.img', 'wb') as f:
        # <-::- Serializa Superblock e grava na memória -::->
        serialized_superblock = pickle.dumps(superblock)
        f.write(serialized_superblock.ljust(BLOCK_SIZE, b'\x00')) # Escreve o superbloco

        # <-::- Serializa bitmap dos blocos e grava na memória -::->
        blocks_bitmap = bitarray([0 for _ in range((INODES_BITMAP_START - BLOCKS_BITMAP_START) * BLOCK_SIZE * 8)])
        blocks_bitmap[0] = 1 # Bloco do root
        serialized_blocks_bitmap = blocks_bitmap.tobytes()
        f.write(serialized_blocks_bitmap.ljust((INODES_BITMAP_START - BLOCKS_BITMAP_START) * BLOCK_SIZE, b'\x00')) # Escreve o bitmap dos blocos

        # <-::- Serializa bitmap dos INodes e grava na memória -::->
        inodes_bitmap = bitarray([0 for _ in range(INODES)])
        inodes_bitmap[0] = 1 # INode do root
        serialized_inodes_bitmap = inodes_bitmap.tobytes()
        f.write(serialized_inodes_bitmap.ljust((DATA_BLOCKS_START - INODES_BITMAP_START) * BLOCK_SIZE, b'\x00')) # Escreve o bitmap dos inodes
        
        # <-::- Criar raiz -::->
        root_dict = pickle.dumps({'.':0, '..':0})
        data_size = len(root_dict)
        root = IndexNode('/', 0, CREATOR, OWNER, data_size, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), 'drwxr-xr-x', [0])

        # <-::- Inserir INode e Bloco na IMG -::->
        f.seek(DATA_BLOCKS_START * BLOCK_SIZE) # Ponteiro do arquivo apontará para o bloco de data da pasta raiz
        f.write(root_dict)

        # <-::- Criar INodes NPY -::->
        inodes_vector = np.zeros(INODES, dtype=object)
        inodes_vector[0] = root
        np.save('inodes.npy', inodes_vector)

create()
