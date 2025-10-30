# Libs
import shlex # Lib usada para tokenizar entrada e reconhecer operações
from bitarray import bitarray # Lib usada para salvar os maps de blocos e inodes
import pickle
import numpy as np
import os

# Files
from functions import archives, directory, common # Arquivos contendo funções (comandos)
from variables import * #constantes
from control import * #classe controle

def absolute_path(f, inode, inodes_array):
    #function para calcular o caminho absoluto a partir do i-node atual
    path = [] #lista com os diretorios
    while inode.index != 0: #sobe na hierarquia ate achar o inode raiz (index==0)
        path.append(inode.name) #add o nome do dir atual na lista
        inode = ctrl.change_dir(f, inode, ['..'], inodes_array) #troca de diretorio
    path.reverse() #inverte para ter a lista do topo para baixo

    if len(path) == 0: return '/' #se lista vazia == raiz
    return '/' + '/'.join(path) #concatena os nomes com '/' 
    

def read_bitmap(file, pos, n): 
    #Func para ler uma secao de bitmap, blocks ou inodes, do arquivo de disco
    file.seek(pos) #move o ponteiro do arquivo 'f' para a posicao inicial do Bitmap no disco
    bitmap = bitarray() 
    bitmap.frombytes(f.read(n)) #lê 'n' bytes (o tamanho total do Bitmap) e converte para uma sequência de bits.
    return list(bitmap) #retorna como uma lista normal

# Arquitetura Atual
# Bloco 0 --> Super bloco
# Blocos 1-32 --> Bitmap de blocos 0/1 -> livres/ocupados => (HDD em Bytes / Tamanho dos blocos = Blocos) / 8 = Bytes necessários para representar estados) / Tamanho dos blocos = Blocos necessários para Bitmap
## Bloco 33 --> Bitmap de inodes 0/1 -> livres/ocupados => Numero de INodes / INodes por bloco / Tamanho dos blocos = Blocos necessários para Bitmap
## Blocos 34-1058 --> INodes em si => Valor arbitrário
# Blocos 1058-131071 (inicia em bloco 0) --> dados (arquivos/diretorios) => Blocos restantes

# <-::- Ler Array de INodes -::->
try:
    #tenta carregar o array de inodes do disco
    inodes_array = np.load('inodes.npy', allow_pickle=True)
except ModuleNotFoundError:
    #se nao for encontrado == formatar disco (disk_manipulate.py)
    exit(f'Erro. Crie o disco primeiramente com "disk_manipulate.py"')

#bloco principal
try:
    #abre o arquivo de disco em modo de leitura e escrita 
    with open('disk.img', 'r+b') as f:
        # <-::- Ler Superbloco -::->
        f.seek(0) #ponteiro para o inicio do disco (superblock)
        sb = pickle.load(f) #carrega o superblock (dict)

        ctrl = Control(sb) #instancia o control passando o superblock carregado

        # <-::- Criar operações para leitura -::->
        df = directory.Directory(ctrl) #funcoes de diretorios
        af = archives.Archives(ctrl) #funcoes de arquivos
        cf = common.Common(ctrl) #funcoes comuns para dir e archives

        #Dicionário de mapeamento: Comandos do usuário -> Métodos correspondentes
        operations = {'mv':cf.mv, # Funções que serão reconhecidas pelo token
                    'ln':cf.ln,  
                    'clear':cf.clear,
                    'exit':cf.exit,
                    'touch':af.touch, 
                    'rm':af.rm, 
                    'echo':af.echo, 
                    'cat':af.cat, 
                    'cp':af.cp, 
                    'mkdir':df.mkdir, 
                    'rmdir':df.rmdir, 
                    'ls':df.ls, 
                    'cd':df.cd
                    }
        
        # <-::- Carregar CWD e Bitmaps -::->
        cwd = [inodes_array[0]] #inicializa com o inode raiz

        #lê o Bitmap de blocos (do início do bitmap de blocos até o início do bitmap de i-nodes)
        blocks_bitmap = read_bitmap(f, sb['blocks_bitmap_start'] * sb['block_size'], (sb['inodes_bitmap_start'] - sb['blocks_bitmap_start']) * sb['block_size'])
        #lê o Bitmap de i-nodes (do início do bitmap de i-nodes até o início dos blocos de dados)
        inodes_bitmap = read_bitmap(f, sb['inodes_bitmap_start'] * sb['block_size'], (sb['data_blocks_start'] - sb['inodes_bitmap_start']) * sb['block_size'])

        os.system('clear') # Limpar terminal

        while True: # Loop para entradas>
            #pede a entrada do user mostrando o caminho absoluto
            entry = input(f"{absolute_path(f, cwd[0], inodes_array)}$ ") # Entrada do terminal
            tokens = shlex.split(entry) # Tokeniza entrada (comandos / argumentos)

            try:
                op = operations[tokens[0]] # Primeiro token sempre será a operação a ser realizada

                op(f, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *tokens[1:])
                # Chama a função de comando, passando o manipulador de arquivo 'f', o CWD, os arrays de estado,
                # e desempacotando o restante dos tokens como argumentos (*tokens[1:])
                
            except KeyError:
                print("Erro. Comando não existente!")
            except (WrongParameters, CantMoveParent, FileAlreadyExists) as e:
                print(e)

except FileNotFoundError:
    exit(f'Erro. Crie o disco primeiramente com "disk_manipulate.py"')
