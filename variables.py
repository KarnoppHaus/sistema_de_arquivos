import math

B = 1
KB = 1024 * B
MB = 1024 * KB
GB = 1024 * MB
TB = 1024 * GB

HDD_CAPACITY =  64 * MB
BLOCK_SIZE = 512 * B
INODES = 1024

CREATOR = 'Theo'
OWNER = 'Theo'

BLOCKS_BITMAP_START = 1
INODES_BITMAP_START = BLOCKS_BITMAP_START + math.ceil(round(((HDD_CAPACITY / BLOCK_SIZE) / 8) / BLOCK_SIZE, 2)) # Quantidade de blocos para representar estado dos inodes + (1 -> inicio do bitmap dos blocos)
DATA_BLOCKS_START = INODES_BITMAP_START + math.ceil(round((INODES / 8) / BLOCK_SIZE, 2)) # + Blocos ocupados pelo Bitmap dos INodes

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