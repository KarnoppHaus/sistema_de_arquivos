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
    #classe para gerenciar alocacao de recursos e i/o de disco
    def __init__(self, superblock):
        #construtor armazena o dict do sb (com infos do layout do disco)
        self.sb = superblock

    def save_bitmap(self, f, blocks_bitmap=None, inodes_bitmap=None):
        """Salvar Bitmaps dentro do disco"""
        #função para escrever os Bitmaps atualizados de volta no arquivo disk.img

        # <-::- Save Blocks Bitmap -::->
        if blocks_bitmap:
            #move o ponteiro do arquivo para a posição de início do Bitmap de Blocos
            f.seek(self.sb['blocks_bitmap_start'] * self.sb['block_size'])
            #converte o bitarray para bytes, preenche o restante do bloco com \x00 e grava no disco
            f.write(bitarray(blocks_bitmap).tobytes().ljust((self.sb['inodes_bitmap_start'] - self.sb['blocks_bitmap_start']) * self.sb['block_size'], b'\x00'))

        # <-::- Save INodes Bitmap -::->
        if inodes_bitmap:
            #move o ponteiro do arquivo para a posição de início do Bitmap de Inodes
            f.seek(self.sb['inodes_bitmap_start'] * self.sb['block_size'])
            #converte o bitarray para bytes, preenche o restante do bloco com \x00 e grava no disco
            f.write(bitarray(inodes_bitmap).tobytes().ljust((self.sb['data_blocks_start'] - self.sb['inodes_bitmap_start']) * self.sb['block_size'], b'\x00'))

    def save_inode(self, inodes_array, inode):
        #Salva o i-node como matriz numpy
        inodes_array[inode.index] = inode
        np.save('inodes.npy', inodes_array)

    def read_blocks(self, f, inode, inodes_array):
        #le o conteúdo de todos os blocos apontados por um i-node e retorna o objeto Python original
        s = b'' #inicia a string de bytes
        if inode.inode_pointer:
            #se for um link, inode aponta para outro inode e le o inode alvo.
            inode = self.read_inode(inodes_array, inode.inode_pointer)

        for block in inode.block_pointers:
            #para cada bloco apontado pelo i-node:
            #calcula a posição exata no disco: (Início da Área de Dados + índice do bloco) * Tamanho do Bloco
            f.seek((self.sb['data_blocks_start'] + block) * self.sb['block_size'])
            s += f.read(self.sb['block_size']) #le o block completo e anexa ao buffer s
        return pickle.loads(s) #desserializa o conteúdo binário concatenado de volta para o objeto Python

    def divide_in_blocks(self, content):
        """Retorna uma tupla com tamanho, numero de blocos e vetor com os conteúdos divididos pelos blocos necessários já completos e serializados (size, blocks, [contents])"""
        serialized_content = pickle.dumps(content)
        serialized_content_size = len(serialized_content)
        #calcula quantos blocks inteiros sao necessarios
        total_blocks = math.ceil(serialized_content_size / self.sb['block_size'])

        serialized_content = serialized_content.ljust(total_blocks * self.sb['block_size'], b'\x00')
        contents = []
        for start in range(total_blocks):
            end = start + 1
            contents.append(serialized_content[start * self.sb['block_size'] : end * self.sb['block_size']])
        return (serialized_content_size, total_blocks, contents)

    def rewrite(self, f, inode, inodes_array, new_content, blocks_bitmap):
        #rotina principal para atualizar ou escrever novo conteúdo em um i-node
        size, blocks, serialized_contents = self.divide_in_blocks(new_content)

        #1- libera blocos antigos
        for block in inode.block_pointers:
            blocks_bitmap[block] = 0

        #2- aloca blocos novos
        #encontra 'blocks' espaços livres no Bitmap e os marca como ocupados (retorna os índices alocados)
        blocks = self.find_empty_place(blocks_bitmap, self.sb['usable_blocks'], blocks)

        inode.block_pointers = blocks #atualiza o i-node para apontar para os novos blocos.

        #3- grava os dados
        for block, content in zip(blocks, serialized_contents):
            blocks_bitmap[block] = 1
            # <-::- Gravar blocos -::->
            f.seek((self.sb['data_blocks_start'] + block) * self.sb['block_size'])
            f.write(content)

        # <-::- Salvar Bitmap dos Blocos -::->
        self.save_bitmap(f, blocks_bitmap) #salva no disk.img
        
        # <-::- Salvar INodes -::->
        self.save_inode(inodes_array, inode) #salva no inodes.npy

    def read_inode(self, inodes_array, inode_index):
        #simplesmente retorna o objeto IndexNode do array pelo seu índice
        return inodes_array[inode_index] 

    def find_empty_place(self, bitmap, limit, times):
        """Retorna vetor de índices livres no Bitmap de entrada"""
        indexes = []
        for index in range(limit):
            if bitmap[index] == 0: #se o bit for 0
                indexes.append(index)
            if times == len(indexes):  #se o número de índices livres requisitados for atingido
                for index in indexes:
                    bitmap[index] = 1 #marca esses índices como OCUPADOS (1) antes de retornar
                return indexes
        raise FullBitmap('O bitmap está cheio!')

    def add_in_folder(self, f, inode, inodes_array, folder, blocks_bitmap):
        #adiciona uma nova entrada (arquivo ou pasta) no dicionário de conteúdo de um diretório pai
        folder_dict = self.read_blocks(f, folder, inodes_array) #le o conteúdo do diretório pai
        folder_dict[inode.name] = inode.index #adiciona a nova entrada: nome -> índice do novo i-node

        self.rewrite(f, folder, inodes_array, folder_dict, blocks_bitmap) #reescreve o dicionário da pasta pai no disco

    def change_dir(self, f, cwd, dirs, inodes_array):
        if len(dirs) == 0: return cwd #se a lista de diretórios estiver vazia, retorna o diretório atual
        if dirs[0] == '':
            cwd = inodes_array[0] #se o caminho começar com '/', volta para o i-node raiz
            dirs.pop(0)
        for dir in dirs:
            #atualiza o cwd para o i-node de destino
            cwd = self.read_inode(inodes_array, self.read_blocks(f, cwd, inodes_array)[dir])
            if cwd.permissions[0] != 'd':
                raise NotFolderINode #verifica se o item é realmente um diretório
        return cwd #retorna o i-node final
    
    def create_folder(self, f, name, inodes_array, inodes_bitmap, folder, blocks_bitmap):
        #rotina de alto nível para criar um novo diretório
        inode_index = (self.find_empty_place(inodes_bitmap, self.sb['inodes'], 1))[0]
        #cria o objeto IndexNode (permissão 'd' para diretório)
        inode = IndexNode(name, inode_index, 'Theo', 'Theo', 0, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), 'drwxr-xr-x')
        folder_content = {'.':inode_index, '..':folder.index} #conteudo inicial da nova pasta . e ..
        self.add_in_folder(f, inode, inodes_array, folder, blocks_bitmap) #nova pasta no dir pai
        self.rewrite(f, inode, inodes_array, folder_content, blocks_bitmap) #grava o conteúdo (. e ..) da nova pasta
        self.save_bitmap(f, inodes_bitmap=inodes_bitmap) #salva o bitmap de inodes
        return inode

    def create_file(self, f, name, inodes_array, inodes_bitmap, folder, blocks_bitmap, content=''):
        #rotina de alto nível para criar um novo arquivo
        inode_index = (self.find_empty_place(inodes_bitmap, self.sb['inodes'], 1))[0] #aloca um i-node livre
        inode = IndexNode(name, inode_index, 'Theo', 'Theo', 0, time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), '-rwxr-xr-x')
        file_content = content #o conteúdo inicial (pode ser vazio)
        self.add_in_folder(f, inode, inodes_array, folder, blocks_bitmap) #adiciona o arquivo ao diretório pai
        self.rewrite(f, inode, inodes_array, file_content, blocks_bitmap) #grava o conteúdo do arquivo no disco
        self.save_bitmap(f, inodes_bitmap=inodes_bitmap) #salva o bitmap de inodes atualizado
        return inode
    
    def create_link_inode(self, name, org_inode, inodes_bitmap):
        #rotina para criar um i-node que aponta para outro i-node (link)
        inode_index = (self.find_empty_place(inodes_bitmap, self.sb['inodes'], 1))[0] #aloca novo inode
        inode = copy.deepcopy(org_inode) 
        inode.name = name #nome do link
        inode.index = inode_index #define o novo indice 
        inode.block_pointers = [] #o link n aponta para blocos de dados
        inode.inode_pointer = org_inode.index #ponteiro aponta para o i-node original
        return inode