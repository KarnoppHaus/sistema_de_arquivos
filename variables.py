import math

B = 1
KB = 1024 * B
MB = 1024 * KB
GB = 1024 * MB
TB = 1024 * GB

HDD_CAPACITY =  64 * MB #tamanho total do disco
BLOCK_SIZE = 512 * B #tamanho do bloco
INODES = 1024 #define o número máximo de i-nodes (e, portanto, o número máximo de arquivos/diretórios) que o sistema suporta

CREATOR = 'Theo'
OWNER = 'Theo'

# O Bloco 0 é sempre reservado para o Superbloco
BLOCKS_BITMAP_START = 1

#Inicio de Bitmap de inodes == Onde termina o Bitmap de Blocos
#Lógica: Ocupa blocos suficientes para representar o estado de todos os blocos de dados
INODES_BITMAP_START = BLOCKS_BITMAP_START + math.ceil(round(((HDD_CAPACITY / BLOCK_SIZE) / 8) / BLOCK_SIZE, 2)) # Quantidade de blocos para representar estado dos inodes + (1 -> inicio do bitmap dos blocos)

#Posição de Início dos Blocos de Dados (Onde termina o Bitmap de I-nodes)
#Lógica: Ocupa blocos suficientes para representar o estado de todos os INODES
DATA_BLOCKS_START = INODES_BITMAP_START + math.ceil(round((INODES / 8) / BLOCK_SIZE, 2)) # + Blocos ocupados pelo Bitmap dos INodes

#Cálculo da quantidade real de blocos de dados disponíveis para arquivos e diretórios
#(HDD_CAPACITY // BLOCK_SIZE): Total de blocos no disco
#- DATA_BLOCKS_START: Subtrai os blocos usados para metadados (Superbloco, Bitmaps)
USABLE_BLOCKS = HDD_CAPACITY // BLOCK_SIZE - DATA_BLOCKS_START # (Fim + 1 pois nao inicia em 0) - Inicio, exemplo: 1-2 -> 3 - 1 = 2 blocos

superblock = {
    'size': HDD_CAPACITY, # Quantidade total do HDD
    'block_size': BLOCK_SIZE,
    'blocks': HDD_CAPACITY // BLOCK_SIZE,
    'usable_blocks': USABLE_BLOCKS,
    'inodes': INODES,
    'blocks_bitmap_start': BLOCKS_BITMAP_START,
    'inodes_bitmap_start': INODES_BITMAP_START,
    'data_blocks_start': DATA_BLOCKS_START
}