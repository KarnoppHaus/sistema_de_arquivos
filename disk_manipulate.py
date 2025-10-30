from variables import *
import pickle
from bitarray import bitarray
from inode import IndexNode
import time
import numpy as np

def create():

    # Função principal responsável por criar e inicializar o disco virtual
    
    # Cria (ou sobrescreve) o arquivo 'disk.img' em modo de escrita binária ('wb')

    with open('disk.img', 'wb') as f:
        # <-::- Serializa Superblock e grava na memória -::->
        serialized_superblock = pickle.dumps(superblock) #Serializa o dicionário 'superblock' para bytes, preparando-o para gravação
        f.write(serialized_superblock.ljust(BLOCK_SIZE, b'\x00')) # Escreve o superbloco

        # <-::- Serializa bitmap dos blocos e grava na memória -::->
        #cria o Bitmap de Blocos: Uma lista de bits com 0s (livre). O tamanho é calculado em 'variables.py'
        blocks_bitmap = bitarray([0 for _ in range((INODES_BITMAP_START - BLOCKS_BITMAP_START) * BLOCK_SIZE * 8)])
        blocks_bitmap[0] = 1 # Bloco do root (marca como ocupado)
        serialized_blocks_bitmap = blocks_bitmap.tobytes() #converte a lista de bits para bytes para gravação.
        f.write(serialized_blocks_bitmap.ljust((INODES_BITMAP_START - BLOCKS_BITMAP_START) * BLOCK_SIZE, b'\x00')) # Escreve o bitmap dos blocos

        # <-::- Serializa bitmap dos INodes e grava na memória -::->
        inodes_bitmap = bitarray([0 for _ in range(INODES)]) #cria o bitmap de inodes com valor 0
        inodes_bitmap[0] = 1 # INode do root (ocupado)
        serialized_inodes_bitmap = inodes_bitmap.tobytes() 
        f.write(serialized_inodes_bitmap.ljust((DATA_BLOCKS_START - INODES_BITMAP_START) * BLOCK_SIZE, b'\x00')) # Escreve o bitmap dos inodes
        
        # <-::- Criar raiz -::->
        #cria o conteúdo interno do diretório raiz: mapeia '.' e '..' para o índice 0 (ele próprio)
        root_dict = pickle.dumps({'.':0, '..':0})
        data_size = len(root_dict)
        #cria o inode para o root
        #com permissoes e horarios e tudo mais
        root = IndexNode('/', 0, CREATOR, OWNER, data_size, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), 'drwxr-xr-x', [0])

        # <-::- Inserir INode e Bloco na IMG -::->
        f.seek(DATA_BLOCKS_START * BLOCK_SIZE) # Ponteiro do arquivo apontará para o bloco de data da pasta raiz
        f.write(root_dict)

        # <-::- Criar INodes NPY -::->
        inodes_vector = np.zeros(INODES, dtype=object)
        inodes_vector[0] = root #insere o i-node raiz na posição 0 do array.
        np.save('inodes.npy', inodes_vector) #salva o array de i-nodes no arquivo para uso futuro.

create()
