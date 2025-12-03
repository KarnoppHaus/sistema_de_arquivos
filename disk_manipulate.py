from variables import *
import pickle
from bitarray import bitarray
from inode import IndexNode
import hashlib
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
        blocks_bitmap[1] = 1 # Bloco do root dir
        blocks_bitmap[2] = 1 # Bloco do etc
        blocks_bitmap[3] = 1 # Bloco do home
        blocks_bitmap[4] = 1 # Bloco do passwd
        serialized_blocks_bitmap = blocks_bitmap.tobytes()
        f.write(serialized_blocks_bitmap.ljust((INODES_BITMAP_START - BLOCKS_BITMAP_START) * BLOCK_SIZE, b'\x00')) # Escreve o bitmap dos blocos

        # <-::- Serializa bitmap dos INodes e grava na memória -::->
        inodes_bitmap = bitarray([0 for _ in range(INODES)])
        inodes_bitmap[0] = 1 # INode do root
        inodes_bitmap[1] = 1 # INode do root dir
        inodes_bitmap[2] = 1 # INode do etc
        inodes_bitmap[3] = 1 # INode do home
        inodes_bitmap[4] = 1 # INode do passwd
        serialized_inodes_bitmap = inodes_bitmap.tobytes()
        f.write(serialized_inodes_bitmap.ljust((DATA_BLOCKS_START - INODES_BITMAP_START) * BLOCK_SIZE, b'\x00')) # Escreve o bitmap dos inodes
        
        # <-::- Criar raiz -::->
        root_dict = pickle.dumps({'.':0, '..':0, 'root':1, 'etc':2, 'home':3})
        data_size = len(root_dict)
        root = IndexNode('/', 0, 'root', 'root', 'root_group',  data_size, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), 'drwxr-xr-x', [0])
        
        rootd_dict = pickle.dumps({'.':1, '..':0})
        data_size = len(rootd_dict)
        rootd = IndexNode('root', 1, 'root', 'root', 'root_group',  data_size, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), 'drwx------', [1])
        
        home_dict = pickle.dumps({'.':3, '..':0})
        data_size = len(home_dict)
        home = IndexNode('home', 3, 'root', 'root', 'root_group',  data_size, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), 'drwxr-xr-x', [3])

        # <-::- Criar /etc/passwd -::->
        etc_dict = pickle.dumps({'.':2, '..':0, 'passwd':4})
        data_size = len(etc_dict)
        etc = IndexNode('etc', 2, 'root', 'root', 'root_group', data_size, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), 'drwxr-xr-x', [2])
        passwd = IndexNode('passwd', 4, 'root', 'root', 'root_group',  0, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), '-rw-r--r--', [4])
        
        # <-::- Inserir INode e Bloco na IMG -::->
        f.seek(DATA_BLOCKS_START * BLOCK_SIZE) # Ponteiro do arquivo apontará para o bloco de data da pasta raiz
        f.write(root_dict)
        
        f.seek(DATA_BLOCKS_START * BLOCK_SIZE + BLOCK_SIZE) # Ponteiro do arquivo apontará para o bloco de data da pasta raiz
        f.write(rootd_dict)
        
        f.seek(DATA_BLOCKS_START * BLOCK_SIZE + (BLOCK_SIZE * 2))
        f.write(etc_dict)
        
        f.seek(DATA_BLOCKS_START * BLOCK_SIZE + (BLOCK_SIZE * 3))
        f.write(home_dict)
        
        f.seek(DATA_BLOCKS_START * BLOCK_SIZE + (BLOCK_SIZE * 4))
        f.write(pickle.dumps(f'root:{hashlib.sha256(ROOT_PASSWD.encode()).hexdigest()}:0:root_group:/root\n'))
        
        # <-::- Criar INodes NPY -::->
        inodes_vector = np.zeros(INODES, dtype=object)
        inodes_vector[0] = root
        inodes_vector[1] = rootd
        inodes_vector[2] = etc
        inodes_vector[3] = home
        inodes_vector[4] = passwd
        np.save('inodes.npy', inodes_vector)

create()
